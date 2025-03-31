import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, TextField, Avatar, Menu, MenuItem, IconButton, Tooltip } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { useNavigate, useLocation } from 'react-router-dom';
import LoginButton from './LoginButton';
import LogoutButton from './LogoutButton';
import SearchIcon from '@mui/icons-material/Search';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

const Header = ({ onSearch, searchQuery, setSearchQuery, userInfo, tokens, onLogout, isAdmin }) => {
  const [error, setError] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [isProcessingCode, setIsProcessingCode] = useState(false);
  const [lastTokenVerification, setLastTokenVerification] = useState(null);
  const TOKEN_VERIFICATION_INTERVAL = 5 * 60 * 1000; // 5 minutes in milliseconds

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    console.log('=== Header Debug Info ===');
    console.log('User Info:', userInfo);
    console.log('Is Admin:', isAdmin);
    console.log('==========================');
  }, [userInfo, isAdmin]);

  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get("code");
    const error = urlParams.get("error");
    const errorDescription = urlParams.get("error_description");

    if (error) {
      console.error('Auth0 error:', error, errorDescription);
      setError(`Authentication error: ${errorDescription || error}`);
      navigate('/', { replace: true });
      return;
    }

    if (code && !isProcessingCode) {
      console.log('Received Auth0 code:', code);
      const processedCodes = JSON.parse(localStorage.getItem('processed_codes') || '[]');
      if (processedCodes.includes(code)) {
        console.log('Code already processed, skipping');
        return;
      }
      setIsProcessingCode(true);
      exchangeCodeForToken(code);
      navigate('/', { replace: true });
    }
  }, [location, navigate, isProcessingCode]);

  const exchangeCodeForToken = async (code) => {
    try {
      const processedCodes = JSON.parse(localStorage.getItem('processed_codes') || '[]');
      if (processedCodes.includes(code)) {
        console.log('Code already processed, skipping');
        return;
      }
      
      const response = await fetch('http://localhost:5001/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to exchange code for tokens');
      }

      const data = await response.json();
      console.log('Received tokens and user info:', {
        hasAccessToken: !!data.tokens?.access_token,
        hasUserInfo: !!data.user
      });
      
      if (data.tokens?.access_token) {
        localStorage.setItem('tokens', JSON.stringify(data.tokens));
        localStorage.setItem('user_info', JSON.stringify(data.user));
        localStorage.setItem('access_token', data.tokens.access_token);
        setLastTokenVerification(Date.now());
        console.log('Stored tokens and user info in localStorage');
      }

      processedCodes.push(code);
      localStorage.setItem('processed_codes', JSON.stringify(processedCodes));

      window.location.reload();
    } catch (error) {
      console.error('Error exchanging code for tokens:', error);
      clearAllData();
      setError(error.message);
      onLogout();
    } finally {
      setIsProcessingCode(false);
    }
  };

  const verifyToken = async () => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      console.log('No access token found in localStorage');
      return;
    }

    const now = Date.now();
    if (lastTokenVerification && (now - lastTokenVerification) < TOKEN_VERIFICATION_INTERVAL) {
      console.log('Using cached token verification');
      return;
    }

    try {
      const response = await fetch('http://localhost:5001/userinfo', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        if (response.status === 401) {
          console.log('Token expired or invalid, clearing data');
          clearAllData();
          return;
        }
        throw new Error('Token verification failed');
      }

      const data = await response.json();
      console.log('Token verified successfully:', {
        hasUserInfo: !!data.user,
        userEmail: data.user?.email
      });
      
      if (data.user) {
        localStorage.setItem('user_info', JSON.stringify(data.user));
        setLastTokenVerification(now);
      }
    } catch (error) {
      console.error('Token verification error:', error);
      clearAllData();
      onLogout();
    }
  };

  useEffect(() => {
    if (userInfo) {
      verifyToken();
    }
  }, [userInfo]);

  const clearAllData = () => {
    localStorage.removeItem('tokens');
    localStorage.removeItem('user_info');
    localStorage.removeItem('access_token');
    localStorage.removeItem('processed_codes');
    setLastTokenVerification(null);
  };

  const handleMenu = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };

  const handleAdminPanel = () => {
    handleClose();
    navigate('/admin');
  };

  const handleLogout = () => {
    handleClose();
    onLogout();
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      p: 2,
      borderBottom: '1px solid #e0e0e0',
      bgcolor: '#ffffff'
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <MenuBookIcon sx={{ fontSize: 32, color: '#1976d2' }} />
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ 
            fontWeight: 600,
            cursor: 'pointer',
            color: '#333333'
          }}
          onClick={() => navigate('/')}
        >
          AnkiCardGen
        </Typography>
      </Box>

      <Box sx={{ 
        display: 'flex', 
        alignItems: 'center',
        gap: 2,
        flexGrow: 1,
        justifyContent: 'center',
        maxWidth: '600px',
        mx: 'auto'
      }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search decks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && onSearch()}
          InputProps={{
            startAdornment: <SearchIcon sx={{ color: '#666666', mr: 1 }} />,
          }}
        />
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {userInfo ? (
          <>
            {isAdmin && (
              <Tooltip title="Admin Panel">
                <IconButton
                  color="inherit"
                  onClick={handleAdminPanel}
                  sx={{ 
                    mr: 1,
                    color: '#1976d2',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.04)'
                    }
                  }}
                >
                  <AdminPanelSettingsIcon />
                </IconButton>
              </Tooltip>
            )}
            <Button
              color="inherit"
              onClick={handleMenu}
              startIcon={
                <Avatar
                  alt={userInfo.name || userInfo.email}
                  src={userInfo.picture || userInfo.db_user?.picture}
                  sx={{ width: 32, height: 32 }}
                />
              }
            >
              {userInfo.name || userInfo.email?.split('@')[0]}
            </Button>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleProfile}>Profile</MenuItem>
              {isAdmin && (
                <MenuItem onClick={handleAdminPanel}>
                  <AdminPanelSettingsIcon sx={{ mr: 1 }} /> Admin Panel
                </MenuItem>
              )}
              <MenuItem onClick={handleLogout}>Logout</MenuItem>
            </Menu>
          </>
        ) : (
          <LoginButton />
        )}
      </Box>
    </Box>
  );
};

export default Header; 