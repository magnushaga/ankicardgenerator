import React, { useState, useEffect } from 'react';
import { Box, Typography, Button } from '@mui/material';
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
import TextbookDashboard from './components/textbooks/TextbookDashboard';
import TextbookAnalyzer from './components/textbooks/TextbookAnalyzer';
import { EditorTestPage } from './editor';
import { verifyToken, clearAuthData, getAccessToken } from './lib/authUtils';

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
      const accessToken = getAccessToken();

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
        // Set a timeout to prevent getting stuck in loading state
        const timeoutPromise = new Promise((resolve) => {
          setTimeout(() => {
            console.log("Token verification timeout - using cached data");
            resolve({ 
              isValid: true, 
              user: savedUserInfo ? JSON.parse(savedUserInfo) : null, 
              error: 'Verification timeout' 
            });
          }, 10000);
        });
        
        // Race the verification against the timeout
        const result = await Promise.race([
          verifyToken(accessToken, true),
          timeoutPromise
        ]);
        
        if (result.isValid && result.user) {
          setUserInfo(result.user);
          // The timestamp is already stored in localStorage by verifyToken
          const lastVerification = localStorage.getItem('last_token_verification');
          if (lastVerification) {
            setLastTokenVerification(parseInt(lastVerification));
          }
        } else if (!result.isValid && result.error === 'Token expired or invalid') {
          console.log('Token expired or invalid, clearing data');
          clearAuthData();
          setUserInfo(null);
          setTokens(null);
        }
      }

      if (savedTokens) {
        setTokens(JSON.parse(savedTokens));
      }
    } catch (error) {
      // Only clear data for JSON parsing errors, not for network errors
      if (error instanceof SyntaxError) {
        console.error('Error parsing saved data, clearing local storage:', error);
        clearAuthData();
      } else {
        console.error('Error loading saved data:', error);
      }
    }
  };

  useEffect(() => {
    loadSavedData();
  }, []);

  // Set up periodic token verification
  useEffect(() => {
    if (userInfo) {
      const interval = setInterval(() => {
        const accessToken = getAccessToken();
        if (accessToken) {
          verifyAuthToken(accessToken);
        }
      }, TOKEN_VERIFICATION_INTERVAL);

      return () => clearInterval(interval);
    }
  }, [userInfo]);

  const verifyAuthToken = async (accessToken) => {
    // Use the shared verifyToken function
    const result = await verifyToken(accessToken);
    if (result.isValid && result.user) {
      setUserInfo(result.user);
      // The timestamp is already stored in localStorage by verifyToken
      const lastVerification = localStorage.getItem('last_token_verification');
      if (lastVerification) {
        setLastTokenVerification(parseInt(lastVerification));
      }
    } else if (!result.isValid && result.error === 'Token expired or invalid') {
      console.log('Token expired or invalid, clearing data');
      clearAuthData();
      setUserInfo(null);
      setTokens(null);
    }
  };

  const handleLogout = () => {
    clearAuthData();
    setUserInfo(null);
    setTokens(null);
    setLastTokenVerification(null);
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
          <Route path="/" element={<LandingPage userInfo={userInfo} isAdmin={isAdmin} onLogout={handleLogout} />} />
          <Route path="/login" element={<Navigate to="/" replace />} />
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
          <Route 
            path="/textbooks" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <TextbookDashboard />
                </Box>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/textbooks/analyze/:id" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1, p: 3 }}>
                  <TextbookAnalyzer />
                </Box>
              ) : (
                <Navigate to="/login" replace />
              )
            } 
          />
          <Route 
            path="/editor/test" 
            element={
              userInfo ? (
                <Box sx={{ flex: 1 }}>
                  <EditorTestPage />
                </Box>
              ) : (
                <Box sx={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                  <Typography variant="h5" sx={{ textAlign: 'center' }}>
                    Please log in to access the editor
                    <br/>
                    <Button 
                      variant="contained" 
                      color="primary"
                      sx={{ mt: 2 }}
                      onClick={() => navigate('/')}
                    >
                      Go to Login
                    </Button>
                  </Typography>
                </Box>
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
