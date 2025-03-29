import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import Header from './components/Header';
import DeckSearch from './components/DeckSearch';
import Profile from './components/Profile';

function AppContent() {
  const [searchQuery, setSearchQuery] = useState('');
  const [userInfo, setUserInfo] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    // Check for Auth0 callback
    const handleCallback = async () => {
      const code = new URLSearchParams(window.location.search).get('code');
      if (code) {
        try {
          console.log('Received Auth0 code:', code);
          const response = await fetch('http://localhost:5001/callback', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to exchange code for token');
          }

          const data = await response.json();
          console.log('Received user data:', data);

          // Store tokens and user info
          setTokens(data.tokens);
          setUserInfo(data.user);
          
          // Store access token in sessionStorage and other data in localStorage
          if (data.tokens?.access_token) {
            sessionStorage.setItem('access_token', data.tokens.access_token);
            console.log('Stored access token in sessionStorage');
          }
          localStorage.setItem('user_info', JSON.stringify(data.user));
          localStorage.setItem('tokens', JSON.stringify(data.tokens));

          // Redirect to stored return URL or profile
          const returnTo = localStorage.getItem('returnTo') || '/profile';
          localStorage.removeItem('returnTo');
          navigate(returnTo);
        } catch (error) {
          console.error('Token exchange error:', error);
          setError(error.message);
        }
      }
    };

    handleCallback();
  }, [navigate]);

  useEffect(() => {
    // Load saved user info and tokens
    const savedUserInfo = localStorage.getItem("user_info");
    const savedTokens = localStorage.getItem("tokens");
    const accessToken = sessionStorage.getItem("access_token");
    
    if (savedUserInfo && savedTokens && accessToken) {
      try {
        setUserInfo(JSON.parse(savedUserInfo));
        setTokens(JSON.parse(savedTokens));
        console.log('Loaded saved user data and tokens');
      } catch (err) {
        console.error('Error parsing stored data:', err);
        clearAllData();
      }
    }
  }, []);

  const handleSearch = () => {
    console.log('Searching for:', searchQuery);
  };

  const clearAllData = () => {
    localStorage.removeItem("user_info");
    localStorage.removeItem("tokens");
    sessionStorage.removeItem("access_token");
    setUserInfo(null);
    setTokens(null);
    setError(null);
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column',
      minHeight: '100vh',
      bgcolor: '#ffffff'
    }}>
      <Header 
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onSearch={handleSearch}
        userInfo={userInfo}
        tokens={tokens}
        onLogout={clearAllData}
      />
      <Routes>
        <Route 
          path="/" 
          element={
            (() => {
              const accessToken = sessionStorage.getItem('access_token');
              console.log('=== App.jsx Debug Info ===');
              console.log('Current User Info:', userInfo);
              console.log('Current Tokens:', tokens);
              console.log('Access Token from Session:', accessToken ? accessToken.substring(0, 20) + '...' : 'Not found');
              console.log('==========================');
              
              return (
                <DeckSearch 
                  userInfo={userInfo}
                  accessToken={accessToken}
                />
              );
            })()
          } 
        />
        <Route 
          path="/profile" 
          element={
            userInfo ? (
              <Profile userInfo={userInfo} />
            ) : (
              <Navigate to="/" replace state={{ from: location }} />
            )
          } 
        />
      </Routes>
    </Box>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}

export default App;
