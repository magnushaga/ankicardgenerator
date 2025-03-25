import React from 'react'
import { useAuth } from '../../contexts/AuthContext'
import {
  Container,
  Paper,
  Typography,
  Box,
  Avatar,
  Grid,
  Button,
} from '@mui/material'
import { Person, Email, CalendarToday, Settings } from '@mui/icons-material'

export function Profile() {
  const { user, signOut } = useAuth()

  if (!user) return null

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 4 }}>
          <Avatar
            sx={{ width: 100, height: 100, mr: 3 }}
            src={`https://ui-avatars.com/api/?name=${user.username}&background=random`}
          >
            <Person sx={{ fontSize: 60 }} />
          </Avatar>
          <Box>
            <Typography variant="h4" component="h1">
              {user.username}
            </Typography>
            <Typography variant="subtitle1" color="text.secondary">
              Member since {new Date(user.created_at).toLocaleDateString()}
            </Typography>
          </Box>
        </Box>

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Email sx={{ mr: 1 }} />
              <Typography variant="body1">
                <strong>Email:</strong> {user.email}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <CalendarToday sx={{ mr: 1 }} />
              <Typography variant="body1">
                <strong>Last Login:</strong>{' '}
                {user.last_login
                  ? new Date(user.last_login).toLocaleString()
                  : 'Never'}
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Settings sx={{ mr: 1 }} />
              <Typography variant="body1">
                <strong>Status:</strong>{' '}
                {user.is_active ? 'Active' : 'Inactive'}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Settings />}
            onClick={() => {/* TODO: Implement settings */}}
          >
            Edit Profile
          </Button>
          <Button
            variant="outlined"
            color="error"
            onClick={signOut}
          >
            Sign Out
          </Button>
        </Box>
      </Paper>
    </Container>
  )
} 