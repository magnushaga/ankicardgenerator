import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error('Missing Supabase environment variables')
}

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

export type User = {
  id: string
  email: string
  username: string
  created_at: string
  last_login: string | null
  is_active: boolean
  preferred_study_time: string | null
  notification_preferences: any | null
  study_goals: any | null
}

export type AuthResponse = {
  user: User
  session: {
    access_token: string
    refresh_token: string
  }
} 