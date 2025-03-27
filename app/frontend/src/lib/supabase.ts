import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY
const frontendUrl = import.meta.env.VITE_FRONTEND_URL
const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5001'

if (!supabaseUrl || !supabaseAnonKey) {
  console.error('Missing Supabase environment variables:', {
    url: supabaseUrl ? 'present' : 'missing',
    key: supabaseAnonKey ? 'present' : 'missing'
  })
  throw new Error('Missing Supabase environment variables')
}

console.log('Initializing Supabase client with URL:', supabaseUrl)
console.log('Frontend URL:', frontendUrl)
console.log('Backend URL:', backendUrl)

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true,
    flowType: 'pkce',
    storage: {
      getItem: (key) => {
        try {
          const item = localStorage.getItem(key)
          return item ? JSON.parse(item) : null
        } catch (error) {
          console.error('Error reading from localStorage:', error)
          return null
        }
      },
      setItem: (key, value) => {
        try {
          localStorage.setItem(key, JSON.stringify(value))
        } catch (error) {
          console.error('Error writing to localStorage:', error)
        }
      },
      removeItem: (key) => {
        try {
          localStorage.removeItem(key)
        } catch (error) {
          console.error('Error removing from localStorage:', error)
        }
      },
    },
  },
})

// Initialize auth state
let isInitialized = false
let currentUser: UserInfo | null = null

// Add session listener
supabase.auth.onAuthStateChange(async (event, session) => {
  console.log('Auth state changed:', event)
  
  if (event === 'SIGNED_IN') {
    if (!isInitialized && session?.user) {
      console.log('Initializing user data from session')
      try {
        // Create initial user data from session
        const user = session.user
        const metadata = user.user_metadata || {}
        
        currentUser = {
          id: user.id,
          email: user.email || '',
          username: metadata.username || metadata.full_name || user.email?.split('@')[0] || '',
          created_at: user.created_at || new Date().toISOString(),
          updated_at: user.updated_at || new Date().toISOString(),
          last_login: user.last_sign_in_at || null,
          is_active: true,
          preferred_study_time: undefined,
          notification_preferences: undefined,
          study_goals: undefined
        }

        // Store the access token
        if (session.access_token) {
          localStorage.setItem('access_token', session.access_token)
        }

        // Sync with backend in background
        syncUserWithBackend(currentUser, session.access_token).catch(error => {
          console.warn('Background sync failed:', error)
        })

        isInitialized = true
      } catch (error) {
        console.error('Error initializing user data:', error)
      }
    }
  } else if (event === 'SIGNED_OUT') {
    console.log('User signed out')
    localStorage.removeItem('access_token')
    currentUser = null
    isInitialized = false
  }
})

// Separate sync function
async function syncUserWithBackend(userData: UserInfo, token: string): Promise<UserInfo> {
  const apiUrl = `${backendUrl}/api/auth/me`
  console.log('Syncing with backend:', apiUrl)

  const response = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    },
    body: JSON.stringify(userData),
    credentials: 'include',
    mode: 'cors'
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(`Backend sync failed: ${errorText}`)
  }

  const syncedUser = await response.json()
  console.log('Successfully synced with backend:', syncedUser)
  currentUser = syncedUser
  return syncedUser
}

export async function getUserInfo(): Promise<UserInfo> {
  console.log('Getting user info')
  
  // If we already have the user data, return it
  if (currentUser) {
    console.log('Returning cached user data:', currentUser)
    return currentUser
  }

  // Otherwise, get the current session
  const { data: { session } } = await supabase.auth.getSession()
  
  if (!session?.user) {
    console.error('No active session')
    throw new Error('No active session')
  }

  // Initialize user data if needed
  if (!isInitialized) {
    const user = session.user
    const metadata = user.user_metadata || {}
    
    currentUser = {
      id: user.id,
      email: user.email || '',
      username: metadata.username || metadata.full_name || user.email?.split('@')[0] || '',
      created_at: user.created_at || new Date().toISOString(),
      updated_at: user.updated_at || new Date().toISOString(),
      last_login: user.last_sign_in_at || null,
      is_active: true,
      preferred_study_time: undefined,
      notification_preferences: undefined,
      study_goals: undefined
    }

    try {
      // Sync with backend
      await syncUserWithBackend(currentUser, session.access_token)
      isInitialized = true
    } catch (error) {
      console.warn('Backend sync failed, using Supabase data:', error)
    }
  }

  if (!currentUser) {
    throw new Error('Failed to initialize user data')
  }

  return currentUser
}

export type User = {
  id: string
  email: string
  username: string
  created_at: string
  updated_at: string
}

export type AuthResponse = {
  user: User
  session: any
}

export type SocialAuthProvider = 'google' | 'github'

export const signInWithProvider = async (provider: SocialAuthProvider) => {
  try {
    console.log('Starting sign in with provider:', provider)
    console.log('Using frontend URL:', frontendUrl)
    
    const { data, error } = await supabase.auth.signInWithOAuth({
      provider,
      options: {
        redirectTo: `${frontendUrl}/auth/callback`,
        queryParams: {
          access_type: 'offline',
          prompt: 'consent',
        },
        skipBrowserRedirect: true // Prevent automatic redirect
      },
    })

    if (error) {
      console.error('Error during OAuth sign in:', error)
      throw error
    }

    if (!data?.url) {
      console.error('No URL returned from OAuth sign in')
      throw new Error('No URL returned from OAuth sign in')
    }

    // Store the code verifier in session storage
    const codeVerifier = localStorage.getItem('supabase-code-verifier')
    if (codeVerifier) {
      sessionStorage.setItem('code_verifier', codeVerifier)
    }

    console.log('Redirecting to provider URL:', data.url)
    window.location.href = data.url
  } catch (error) {
    console.error('Error during OAuth sign in:', error)
    throw error
  }
}

export const handleAuthCallback = async () => {
  try {
    console.log('Starting auth callback handling')
    
    // Get the code from the URL
    const params = new URLSearchParams(window.location.search)
    const code = params.get('code')
    
    if (!code) {
      throw new Error('No authorization code found')
    }

    // Get the code verifier from session storage
    const codeVerifier = sessionStorage.getItem('code_verifier')
    console.log('Retrieved code verifier:', codeVerifier ? 'present' : 'missing')
    
    if (!codeVerifier) {
      throw new Error('No code verifier found in session storage')
    }
    
    // Exchange the code for a session
    console.log('Exchanging code for session with code verifier')
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (error) {
      console.error('Error exchanging code for session:', error)
      throw error
    }
    
    if (!data.session) {
      console.error('No session found')
      throw new Error('No session found')
    }

    // Store the access token
    if (data.session.access_token) {
      localStorage.setItem('access_token', data.session.access_token)
    }
    
    // Clean up the code verifier
    sessionStorage.removeItem('code_verifier')
    
    console.log('Auth callback successful:', data.session)
    return { session: data.session }
  } catch (error) {
    console.error('Error handling auth callback:', error)
    // Clean up on error
    sessionStorage.removeItem('code_verifier')
    throw error
  }
}

// Add a function to check if we're in a callback
export const isAuthCallback = () => {
  const params = new URLSearchParams(window.location.search)
  return params.has('code')
}

// Add a function to handle initial auth state
export const initializeAuth = async () => {
  try {
    // If we're in a callback, handle it
    if (isAuthCallback()) {
      return handleAuthCallback()
    }
    
    // Otherwise, try to recover the session
    const { data: { session }, error } = await supabase.auth.getSession()
    if (error) throw error
    return { session }
  } catch (error) {
    console.error('Error initializing auth:', error)
    throw error
  }
}

interface UserInfo {
  id: string
  email: string
  username: string
  created_at: string
  updated_at: string
  last_login: string | null
  is_active: boolean
  preferred_study_time?: string
  notification_preferences?: any
  study_goals?: any
}

export const getStoredToken = () => {
  return localStorage.getItem('access_token')
}

export const removeStoredToken = () => {
  localStorage.removeItem('access_token')
} 