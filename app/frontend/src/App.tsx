import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/auth/ProtectedRoute'
import { LoginForm } from './components/auth/LoginForm'
import { SignupForm } from './components/auth/SignupForm'
import { OAuthCallback } from './components/auth/OAuthCallback'
import { Dashboard } from './components/Dashboard'
import { Navigation } from './components/Navigation'

function App() {
  return (
    <Router>
      <AuthProvider>
        <Navigation />
        <Routes>
          <Route path="/login" element={<LoginForm />} />
          <Route path="/signup" element={<SignupForm />} />
          <Route path="/auth/callback" element={<OAuthCallback />} />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
