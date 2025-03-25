import React from 'react'
import { Button, Stack } from '@mui/material'
import { useAuth } from '../../contexts/AuthContext'
import { SocialAuthProvider } from '../../lib/supabase'

interface SocialAuthProps {
  onSuccess?: () => void
  onError?: (error: Error) => void
}

export const SocialAuth: React.FC<SocialAuthProps> = ({ onSuccess, onError }) => {
  const { signInWithProvider } = useAuth()

  const handleSocialLogin = async (provider: SocialAuthProvider) => {
    try {
      await signInWithProvider(provider)
      onSuccess?.()
    } catch (error) {
      onError?.(error as Error)
    }
  }

  return (
    <Stack spacing={2} width="100%">
      <Button
        variant="outlined"
        color="primary"
        onClick={() => handleSocialLogin('google')}
        fullWidth
      >
        Continue with Google
      </Button>
      <Button
        variant="outlined"
        color="primary"
        onClick={() => handleSocialLogin('github')}
        fullWidth
      >
        Continue with GitHub
      </Button>
      <Button
        variant="outlined"
        color="primary"
        onClick={() => handleSocialLogin('facebook')}
        fullWidth
      >
        Continue with Facebook
      </Button>
      <Button
        variant="outlined"
        color="primary"
        onClick={() => handleSocialLogin('twitter')}
        fullWidth
      >
        Continue with Twitter
      </Button>
    </Stack>
  )
} 