import React, { useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import { SocialAuth } from './SocialAuth'
import {
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Box,
  Divider,
  Alert,
} from '@mui/material'

export const SignupForm: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { signUp } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)

    try {
      await signUp(email, password, username)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Sign Up
          </Typography>
          
          {location.state?.error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {location.state.error}
            </Alert>
          )}
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              disabled={loading}
              sx={{ mt: 3 }}
            >
              {loading ? 'Signing up...' : 'Sign Up'}
            </Button>
          </form>

          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Already have an account?{' '}
              <Button
                color="primary"
                onClick={() => navigate('/login')}
                sx={{ textTransform: 'none' }}
              >
                Login
              </Button>
            </Typography>
          </Box>

          <Divider sx={{ my: 3 }}>or</Divider>

          <SocialAuth
            onSuccess={() => navigate('/dashboard')}
            onError={(err) => setError(err.message)}
          />
        </Paper>
      </Box>
    </Container>
  )
} 