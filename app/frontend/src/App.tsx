import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { LoginForm } from './components/auth/LoginForm'
import { SignupForm } from './components/auth/SignupForm'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { useAuth } from './contexts/AuthContext'
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material'

function Dashboard() {
  const { user, signOut } = useAuth()

  return (
    <Container>
      <Typography variant="h4" component="h1" gutterBottom>
        Welcome, {user?.username}!
      </Typography>
      <Button variant="contained" color="secondary" onClick={signOut}>
        Sign Out
      </Button>
    </Container>
  )
}

function Navigation() {
  const { user } = useAuth()

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          AnkiCard Generator
        </Typography>
        {user ? (
          <Button color="inherit" href="/dashboard">
            Dashboard
          </Button>
        ) : (
          <>
            <Button color="inherit" href="/login">
              Login
            </Button>
            <Button color="inherit" href="/signup">
              Sign Up
            </Button>
          </>
        )}
      </Toolbar>
    </AppBar>
  )
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Navigation />
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          <Route path="/signup" element={<SignupForm />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App
