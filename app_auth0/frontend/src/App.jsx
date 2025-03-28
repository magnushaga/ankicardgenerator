import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Header from './components/Header';
import DeckSearch from './components/DeckSearch';
import Profile from './components/Profile';

function AppContent() {
  const [searchQuery, setSearchQuery] = useState('');
  const [userInfo, setUserInfo] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [error, setError] = useState(null);
  const location = useLocation();

  useEffect(() => {
    // Load saved user info and tokens
    const savedUserInfo = localStorage.getItem("user_info");
    const savedTokens = localStorage.getItem("tokens");
    const accessToken = sessionStorage.getItem("access_token");
    
    if (savedUserInfo && savedTokens && accessToken) {
      try {
        setUserInfo(JSON.parse(savedUserInfo));
        setTokens(JSON.parse(savedTokens));
      } catch (err) {
        console.error('Error parsing stored data:', err);
        clearAllData();
      }
    }
  }, []);

  const handleSearch = () => {
    // The search functionality is handled in the DeckSearch component
    console.log('Searching for:', searchQuery);
  };

  const clearAllData = () => {
    // Clear all stored data
    sessionStorage.removeItem("processed_code");
    sessionStorage.removeItem("access_token");
    sessionStorage.removeItem("id_token");
    localStorage.removeItem("user_info");
    localStorage.removeItem("tokens");
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
        <Route path="/" element={<DeckSearch />} />
        <Route 
          path="/profile" 
          element={
            userInfo ? (
              <Profile />
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
