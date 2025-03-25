import React, { createContext, useContext, useEffect, useState } from 'react'
import { 
  supabase, 
  User, 
  AuthResponse, 
  SocialAuthProvider, 
  signInWithProvider as supabaseSignInWithProvider, 
  handleAuthCallback,
  getUserInfo,
  getStoredToken,
  removeStoredToken
} from '../lib/supabase'

interface AuthContextType {
  user: User | null
  loading: boolean
  signIn: (email: string, password: string) => Promise<AuthResponse>
  signUp: (email: string, password: string, username: string) => Promise<AuthResponse>
  signOut: () => Promise<void>
  signInWithProvider: (provider: SocialAuthProvider) => Promise<void>
  handleOAuthCallback: () => Promise<AuthResponse>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check active sessions and sets the user
    const initializeAuth = async () => {
      try {
        const token = getStoredToken()
        if (token) {
          const userData = await getUserInfo()
          setUser(userData)
        } else {
          const { data: { session } } = await supabase.auth.getSession()
      if (session?.user) {
            const userData = await getUserInfo()
            setUser(userData)
      } else {
            setUser(null)
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    initializeAuth()

    // Listen for changes on auth state (logged in, signed out, etc.)
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.user) {
        try {
          const userData = await getUserInfo()
          setUser(userData)
        } catch (error) {
          console.error('Error fetching user data on auth state change:', error)
          setUser(null)
        }
      } else {
        setUser(null)
        removeStoredToken()
      }
      setLoading(false)
    })

    return () => subscription.unsubscribe()
  }, [])

  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    if (!data.user) throw new Error('No user returned from sign in')
    
    const userData = await getUserInfo()
    return {
      user: userData,
      session: data.session
    }
  }

  const signUp = async (email: string, password: string, username: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
      options: {
        data: {
          username,
        },
      },
    })
    if (error) throw error
    if (!data.user) throw new Error('No user returned from sign up')
    if (!data.session) throw new Error('No session returned from sign up')
    
    const userData = await getUserInfo()
    return {
      user: userData,
      session: data.session
    }
  }

  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
    setUser(null)
    removeStoredToken()
  }

  const signInWithProvider = async (provider: SocialAuthProvider) => {
    try {
      await supabaseSignInWithProvider(provider)
    } catch (error) {
      console.error('Error in signInWithProvider:', error)
      throw error
    }
  }

  const handleOAuthCallback = async () => {
    try {
      console.log('Handling OAuth callback in AuthContext')
      
      // Get the code from the URL
      const params = new URLSearchParams(window.location.search)
      const code = params.get('code')
      
      if (!code) {
        console.error('No authorization code found in URL')
        throw new Error('No authorization code found')
      }
      
      console.log('Found authorization code, exchanging for session')
      
      // Exchange the code for a session
      const { data: { session }, error } = await supabase.auth.exchangeCodeForSession(code)
      
      if (error) {
        console.error('Error exchanging code for session:', error)
        throw error
      }
      
      if (!session) {
        console.error('No session returned from code exchange')
        throw new Error('No session found')
      }
      
      console.log('Session established:', session)
      console.log('Session access token:', session.access_token)
      
      // Store the access token
      if (session.access_token) {
        localStorage.setItem('access_token', session.access_token)
        console.log('Stored access token in localStorage')
      }
      
      // Get user data from our backend
      console.log('Fetching user data from backend')
      try {
        const userData = await getUserInfo()
        console.log('Successfully got user data:', userData)
        
        // Update the user state
        setUser(userData)
        console.log('Updated user state in context')
        
        return {
          user: userData,
          session
        }
      } catch (error) {
        console.error('Error getting user info:', error)
        // Create a basic user object from session data
        const basicUser: User = {
          id: session.user.id,
          email: session.user.email || '',
          username: session.user.user_metadata?.username || session.user.email?.split('@')[0] || '',
          created_at: session.user.created_at || new Date().toISOString(),
          updated_at: session.user.updated_at || new Date().toISOString()
        }
        
        // Update the user state with basic data
        setUser(basicUser)
        console.log('Updated user state with basic data')
        
        return {
          user: basicUser,
          session
        }
      }
    } catch (error) {
      console.error('Error in handleOAuthCallback:', error)
      throw error
    }
  }

  const value = {
    user,
    loading,
    signIn,
    signUp,
    signOut,
    signInWithProvider,
    handleOAuthCallback,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 