import React, { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Box, CircularProgress, Typography, Alert } from '@mui/material'
import { useAuth } from '../../contexts/AuthContext'

export const OAuthCallback: React.FC = () => {
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [status, setStatus] = useState<string>('Completing Authentication...')
  const navigate = useNavigate()
  const location = useLocation()
  const { handleOAuthCallback } = useAuth()

  useEffect(() => {
    const handleCallback = async () => {
      try {
        console.log('Starting OAuth callback handling')
        console.log('Current URL:', window.location.href)
        
        const params = new URLSearchParams(location.search)
        const code = params.get('code')
        
        if (!code) {
          throw new Error('No authorization code found')
        }

        setStatus('Exchanging authorization code...')
        console.log('Exchanging code for session...')
        const { session, user } = await handleOAuthCallback()
        
        if (!session || !user) {
          throw new Error('Failed to establish session or get user data')
        }

        setStatus('Setting up your account...')
        console.log('Session established successfully:', session)
        console.log('User data:', user)
        
        // Store the session and user data
        localStorage.setItem('session', JSON.stringify(session))
        localStorage.setItem('user', JSON.stringify(user))
        
        setStatus('Redirecting to dashboard...')
        // Redirect to dashboard
        navigate('/dashboard', { replace: true })
      } catch (error) {
        console.error('Error in OAuth callback:', error)
        setError(error instanceof Error ? error.message : 'Authentication failed')
        setStatus('Authentication failed')
        // Redirect to login with error
        setTimeout(() => {
          navigate('/login', { 
            state: { error: error instanceof Error ? error.message : 'Authentication failed' },
            replace: true 
          })
        }, 2000)
      } finally {
        setLoading(false)
      }
    }

    handleCallback()
  }, [navigate, location, handleOAuthCallback])

  if (loading) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        gap={2}
      >
        <CircularProgress />
        <Typography variant="h6">{status}</Typography>
        <Typography variant="body2" color="text.secondary">
          Please wait while we complete your sign-in
        </Typography>
      </Box>
    )
  }

  if (error) {
    return (
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
        gap={2}
      >
        <Alert severity="error">{error}</Alert>
        <Typography variant="body2" color="text.secondary">
          Redirecting to login...
        </Typography>
      </Box>
    )
  }

  return null
} 