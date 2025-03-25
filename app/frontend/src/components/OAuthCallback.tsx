import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { handleAuthCallback } from '../lib/supabase'

export default function OAuthCallback() {
  const navigate = useNavigate()

  useEffect(() => {
    const processCallback = async () => {
      try {
        console.log('Starting OAuth callback handling')
        console.log('Current URL:', window.location.href)

        // Handle the callback
        const { session } = await handleAuthCallback()
        
        if (!session) {
          console.error('No session after callback')
          navigate('/login')
          return
        }

        console.log('OAuth callback successful, redirecting to dashboard')
        navigate('/dashboard')
      } catch (error) {
        console.error('Error in OAuth callback:', error)
        navigate('/login')
      }
    }

    processCallback()
  }, [navigate])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="text-center">
        <h2 className="text-xl font-semibold mb-4">Completing sign in...</h2>
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
      </div>
    </div>
  )
} 