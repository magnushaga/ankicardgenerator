import React from 'react'
import { Container, Typography, Box, Button } from '@mui/material'
import { useAuth } from '../contexts/AuthContext'

export const Dashboard: React.FC = () => {
  const { user, signOut } = useAuth()

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome, {user?.username}!
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          This is your dashboard where you can manage your Anki cards and study sessions.
        </Typography>
      </Box>

      <Box sx={{ mt: 4 }}>
        <Button
          variant="contained"
          color="secondary"
          onClick={signOut}
          sx={{ mt: 2 }}
        >
          Sign Out
        </Button>
      </Box>
    </Container>
  )
} 