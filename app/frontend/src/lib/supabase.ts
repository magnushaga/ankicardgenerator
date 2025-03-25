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
        const item = localStorage.getItem(key)
        return item ? JSON.parse(item) : null
      },
      setItem: (key, value) => {
        localStorage.setItem(key, JSON.stringify(value))
      },
      removeItem: (key) => {
        localStorage.removeItem(key)
      },
    },
  },
})

// Add session listener
supabase.auth.onAuthStateChange((event, session) => {
  console.log('Auth state changed:', event, session)
  if (event === 'SIGNED_IN') {
    console.log('User signed in:', session?.user)
    // Store the access token
    if (session?.access_token) {
      localStorage.setItem('access_token', session.access_token)
    }
  } else if (event === 'SIGNED_OUT') {
    console.log('User signed out')
    localStorage.removeItem('access_token')
  }
})

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
    
    // Exchange the code for a session
    const { data: { session }, error } = await supabase.auth.exchangeCodeForSession(code)
    
    if (error) {
      console.error('Error exchanging code for session:', error)
      throw error
    }
    
    if (!session) {
      console.error('No session found')
      throw new Error('No session found')
    }

    // Store the access token
    if (session.access_token) {
      localStorage.setItem('access_token', session.access_token)
    }
    
    console.log('Auth callback successful:', session)
    return { session }
  } catch (error) {
    console.error('Error handling auth callback:', error)
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

export async function getUserInfo(): Promise<UserInfo> {
  try {
    console.log('Starting getUserInfo')
    
    // Get the current session
    const { data: { session }, error: sessionError } = await supabase.auth.getSession()
    if (sessionError) {
      console.error('Error getting session:', sessionError)
      throw sessionError
    }
    
    if (!session) {
      console.error('No active session found')
      throw new Error('No active session')
    }

    console.log('Got session:', session)
    console.log('Session access token:', session.access_token)

    // First try to get user info from our backend
    const apiUrl = `${backendUrl}/api/auth/me`
    console.log('Fetching user info from backend:', apiUrl)
    
    try {
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        credentials: 'include'
      })

      console.log('Backend response status:', response.status)
      console.log('Backend response headers:', Object.fromEntries(response.headers.entries()))

      if (response.ok) {
        const userData = await response.json()
        console.log('Got user data from backend:', userData)
        return userData
      }

      const errorText = await response.text()
      console.error('Backend request failed:', {
        status: response.status,
        statusText: response.statusText,
        error: errorText
      })
    } catch (fetchError) {
      console.error('Error fetching from backend:', fetchError)
    }
    
    // If backend request fails, create a user profile from Supabase data
    const supabaseUser = session.user
    console.log('Creating user from Supabase data:', supabaseUser)
    
    const userData: UserInfo = {
      id: supabaseUser.id,
      email: supabaseUser.email || '',
      username: supabaseUser.user_metadata?.username || supabaseUser.email?.split('@')[0] || '',
      created_at: supabaseUser.created_at || new Date().toISOString(),
      updated_at: supabaseUser.updated_at || new Date().toISOString(),
      last_login: supabaseUser.last_sign_in_at || null,
      is_active: true,
      preferred_study_time: undefined,
      notification_preferences: undefined,
      study_goals: undefined
    }

    console.log('Created user data from Supabase:', userData)

    // Try to create/update the user in our backend
    try {
      console.log('Attempting to create/update user in backend')
      const createResponse = await fetch(apiUrl, {
    method: 'POST',
    headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData),
        credentials: 'include'
      })

      console.log('Create/update response status:', createResponse.status)
      
      if (createResponse.ok) {
        const createdUser = await createResponse.json()
        console.log('Successfully created/updated user in backend:', createdUser)
        return createdUser
      } else {
        const errorText = await createResponse.text()
        console.error('Failed to create/update user in backend:', {
          status: createResponse.status,
          statusText: createResponse.statusText,
          error: errorText
        })
      }
    } catch (error) {
      console.error('Error creating user profile:', error)
    }

    // If all else fails, return the basic user data
    console.log('Returning basic user data')
    return userData
  } catch (error) {
    console.error('Error in getUserInfo:', error)
    throw error
  }
}

export const getStoredToken = () => {
  return localStorage.getItem('access_token')
}

export const removeStoredToken = () => {
  localStorage.removeItem('access_token')
} 