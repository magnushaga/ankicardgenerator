import React, { useState, useEffect } from 'react';
import { Box, Typography } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { ThemeProvider } from './lib/ThemeContext';
import Header from './components/Header';
import DeckSearch from './components/DeckSearch';
import Profile from './components/Profile';
import AnkiDeckViewer from './components/AnkiDeckViewer';
import DeckHierarchyViewer from './components/DeckHierarchyViewer';
import DeckViewer from './components/DeckViewer';
import StudyDeck from './components/StudyDeck';
import AdminDashboard from './components/AdminDashboard';
import LogoutButton from './components/LogoutButton';
import LandingPage from './components/LandingPage';
import CreateDeck from './components/CreateDeck';

function AppContent() {
  const [searchQuery, setSearchQuery] = useState('');
  const [userInfo, setUserInfo] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [error, setError] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [lastTokenVerification, setLastTokenVerification] = useState(null);
  const TOKEN_VERIFICATION_INTERVAL = 5 * 60 * 1000; // 5 minutes in milliseconds

  const loadSavedData = async () => {
    try {
      const savedUserInfo = localStorage.getItem('user_info');
      const savedTokens = localStorage.getItem('tokens');
      const accessToken = localStorage.getItem('access_token');

      console.log('=== App.jsx Debug Info ===');
      console.log('Current User Info:', savedUserInfo ? JSON.parse(savedUserInfo) : null);
      console.log('Current Tokens:', savedTokens ? JSON.parse(savedTokens) : null);
      console.log('Access Token from localStorage:', accessToken ? 'Found' : 'Not found');
      console.log('==========================');

      if (savedUserInfo) {
        const parsedUserInfo = JSON.parse(savedUserInfo);
        setUserInfo(parsedUserInfo);
      }

      if (accessToken) {
        const now = Date.now();
        if (!lastTokenVerification || (now - lastTokenVerification) >= TOKEN_VERIFICATION_INTERVAL) {
          // Verify token with backend
          const response = await fetch('http://localhost:5001/userinfo', {
            headers: {
              'Authorization': `Bearer ${accessToken}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            if (data.user) {
              setUserInfo(data.user);
              localStorage.setItem('user_info', JSON.stringify(data.user));
              setLastTokenVerification(now);
            }
          } else if (response.status === 401) {
            console.log('Token expired or invalid, clearing data');
            clearAllData();
          }
        }
      }

      if (savedTokens) {
        setTokens(JSON.parse(savedTokens));
      }
    } catch (error) {
      console.error('Error loading saved data:', error);
      clearAllData();
    }
  };

  useEffect(() => {
    loadSavedData();
  }, []);

  // Set up periodic token verification
  useEffect(() => {
    if (userInfo) {
      const interval = setInterval(() => {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
          verifyToken(accessToken);
        }
      }, TOKEN_VERIFICATION_INTERVAL);

      return () => clearInterval(interval);
    }
  }, [userInfo]);

  const verifyToken = async (accessToken) => {
    try {
      const response = await fetch('http://localhost:5001/userinfo', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        if (data.user) {
          setUserInfo(data.user);
          localStorage.setItem('user_info', JSON.stringify(data.user));
          setLastTokenVerification(Date.now());
        }
      } else if (response.status === 401) {
        console.log('Token expired or invalid, clearing data');
        clearAllData();
      }
    } catch (error) {
      console.error('Token verification error:', error);
      clearAllData();
    }
  };

  const clearAllData = () => {
    localStorage.removeItem('tokens');
    localStorage.removeItem('user_info');
    localStorage.removeItem('access_token');
    localStorage.removeItem('processed_codes');
    setUserInfo(null);
    setTokens(null);
    setLastTokenVerification(null);
  };

  const handleLogout = () => {
    clearAllData();
  };

  const handleLoginSuccess = async (user, tokens) => {
    console.log('Login successful, updating state with user info:', user);
    
    // Update state with user info and tokens
    setUserInfo(user);
    setTokens(tokens);
    setIsAuthenticated(true);
    
    // Ensure state updates are processed
    await new Promise(resolve => setTimeout(resolve, 0));
    
    // Trigger admin status check
    await checkAdminStatus();
  };

  const handleSearch = () => {
    console.log('Searching for:', searchQuery);
  };

  const checkAdminStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        console.log('No access token found for admin check');
        setIsAdmin(false);
        return;
      }

      console.log('Checking admin status...');
      console.log('Token format:', token.substring(0, 20) + '...');
      
      // First verify the token is valid by getting user info
      const userInfoResponse = await fetch('http://localhost:5001/userinfo', {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!userInfoResponse.ok) {
        console.log('Token verification failed:', userInfoResponse.status);
        setIsAdmin(false);
        return;
      }

      const userInfoData = await userInfoResponse.json();
      console.log('User info verified:', userInfoData);

      console.log('Checking admin status...');
      const response = await fetch('http://localhost:5001/api/admin/check', {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('Admin check response:', response.status);
      const data = await response.json();
      console.log('Admin check data:', data);

      if (response.ok) {
        setIsAdmin(data.is_admin);
        if (data.is_admin) {
          console.log('User is an admin with roles:', data.roles);
          // Update user info with admin details
          const updatedUserInfo = {
            ...userInfoData.user,
            isAdmin: true,
            adminRoles: data.roles
          };
          setUserInfo(updatedUserInfo);
          localStorage.setItem('user_info', JSON.stringify(updatedUserInfo));
        } else {
          console.log('User is not an admin');
          // Update user info to reflect non-admin status
          const updatedUserInfo = {
            ...userInfoData.user,
            isAdmin: false,
            adminRoles: []
          };
          setUserInfo(updatedUserInfo);
          localStorage.setItem('user_info', JSON.stringify(updatedUserInfo));
        }
      } else {
        console.log('Admin check failed:', response.status);
        console.error('Admin check error:', data);
        setIsAdmin(false);
        // Update user info to reflect non-admin status
        const updatedUserInfo = {
          ...userInfoData.user,
          isAdmin: false,
          adminRoles: []
        };
        setUserInfo(updatedUserInfo);
        localStorage.setItem('user_info', JSON.stringify(updatedUserInfo));
      }
    } catch (err) {
      console.error('Error checking admin status:', err);
      setIsAdmin(false);
      // Don't update user info on error to prevent data loss
    }
  };

  useEffect(() => {
    if (userInfo) {
      console.log('User info updated, checking admin status...');
      checkAdminStatus();
    }
  }, [userInfo]);

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      minHeight: '100vh',
      bgcolor: 'background.default'
    }}>
      <Header 
        onSearch={handleSearch}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        userInfo={userInfo}
        tokens={tokens}
        onLogout={handleLogout}
        isAdmin={isAdmin}
        onLoginSuccess={handleLoginSuccess}
      />
      <Box sx={{ flex: 1 }}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route
            path="/create-deck"
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <CreateDeck />
                </Box>
              ) : (
                <Navigate to="/login" state={{ from: location }} replace />
              )
            }
          />
          <Route 
            path="/dashboard" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <DeckSearch />
                </Box>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/profile" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <Profile userInfo={userInfo} />
                </Box>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/admin" 
            element={
              isAdmin ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <AdminDashboard />
                </Box>
              ) : (
                <Navigate to="/dashboard" replace />
              )
            } 
          />
          <Route 
            path="/study/:deckId" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <StudyDeck />
                </Box>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/deck/:deckId" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <DeckViewer />
                </Box>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/hierarchy/:deckId" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <DeckHierarchyViewer />
                </Box>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/anki/:deckId" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <AnkiDeckViewer />
                </Box>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
        </Routes>
      </Box>
      <Box 
        component="footer" 
        sx={{ 
          py: 2, 
          px: 3, 
          textAlign: 'center',
          borderTop: '1px solid',
          borderColor: 'divider'
        }}
      >
        <Typography variant="body2" color="text.secondary">
          © Magnus Kobbeltvedt Haga 2025
        </Typography>
      </Box>
    </Box>
  );
}

function App() {
  return (
    <ThemeProvider>
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  );
}

export default App;
