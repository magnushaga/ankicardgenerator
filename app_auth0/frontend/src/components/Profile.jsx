import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Box, Typography, Button, Avatar, Paper, Divider } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';

function Profile() {
  const [userInfo, setUserInfo] = useState(null);
  const [tokens, setTokens] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get("code");

    if (code) {
      // Only exchange code if we haven't already processed it
      const processedCode = sessionStorage.getItem("processed_code");
      if (code !== processedCode) {
        sessionStorage.setItem("processed_code", code);
        exchangeCodeForToken(code);
      }
      // Clean up the URL after processing the code
      navigate('/profile', { replace: true });
    }
  }, [location, navigate]);

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

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Clear local application data first
      clearAllData();

      // Call backend logout endpoint
      const response = await fetch('http://localhost:5001/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          returnTo: 'http://localhost:5173'
        })
      });

      if (!response.ok) {
        throw new Error('Logout failed');
      }

      const data = await response.json();

      // Redirect to Auth0 logout URL
      if (data.logout_url) {
        window.location.href = data.logout_url;
      }
    } catch (error) {
      setError('Error during logout');
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const exchangeCodeForToken = async (code) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch('http://localhost:5001/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          redirect_uri: 'http://localhost:5173/profile',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to exchange code for token');
      }

      const data = await response.json();
      
      if (!data.tokens || !data.user) {
        throw new Error('Invalid response format from server');
      }

      // Store tokens and user info
      setTokens(data.tokens);
      setUserInfo(data.user);
      
      // Store in storage
      sessionStorage.setItem('access_token', data.tokens.access_token);
      sessionStorage.setItem('id_token', data.tokens.id_token);
      localStorage.setItem('user_info', JSON.stringify(data.user));
      localStorage.setItem('tokens', JSON.stringify(data.tokens));
      
    } catch (error) {
      console.error('Error:', error);
      setError(error.message);
      clearAllData();
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const savedUserInfo = localStorage.getItem("user_info");
    const savedTokens = localStorage.getItem("tokens");
    if (savedUserInfo && savedTokens) {
      setUserInfo(JSON.parse(savedUserInfo));
      setTokens(JSON.parse(savedTokens));
    }
  }, []);

  if (isLoading) {
    return (
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontFamily: 'Arial, sans-serif'
      }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ 
        p: 3,
        maxWidth: 800,
        mx: 'auto',
        mt: 4
      }}>
        <Paper sx={{ p: 3, bgcolor: '#fff5f5' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      </Box>
    );
  }

  if (!userInfo) {
    return (
      <Box sx={{ 
        p: 3,
        maxWidth: 800,
        mx: 'auto',
        mt: 4
      }}>
        <Paper sx={{ 
          p: 4, 
          textAlign: 'center',
          bgcolor: '#f8f8f8'
        }}>
          <Typography variant="h5" gutterBottom>
            Please log in to view your profile
          </Typography>
          <Typography color="text.secondary">
            You can log in using the button in the header
          </Typography>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      p: 3,
      maxWidth: 800,
      mx: 'auto',
      mt: 4
    }}>
      <Paper sx={{ p: 4 }}>
        {/* Profile Header */}
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          mb: 4
        }}>
          {userInfo.picture ? (
            <Avatar 
              src={userInfo.picture} 
              alt={userInfo.name}
              sx={{ 
                width: 120, 
                height: 120,
                mb: 2,
                border: '3px solid #000000'
              }}
            />
          ) : (
            <AccountCircleIcon sx={{ 
              fontSize: 120, 
              mb: 2,
              color: '#000000'
            }} />
          )}
          <Typography variant="h4" gutterBottom>
            {userInfo.name}
          </Typography>
          <Typography color="text.secondary" gutterBottom>
            {userInfo.email}
          </Typography>
          <Button
            variant="outlined"
            color="error"
            startIcon={<LogoutIcon />}
            onClick={handleLogout}
            disabled={isLoading}
            sx={{ mt: 2 }}
          >
            {isLoading ? 'Logging out...' : 'Logout'}
          </Button>
        </Box>

        <Divider sx={{ my: 4 }} />

        {/* User Information */}
        <Box>
          <Typography variant="h6" gutterBottom>
            Account Information
          </Typography>
          <Box sx={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: 2
          }}>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                Email Verified
              </Typography>
              <Typography>
                {userInfo.email_verified ? 'Yes' : 'No'}
              </Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                Last Updated
              </Typography>
              <Typography>
                {new Date(userInfo.updated_at).toLocaleDateString()}
              </Typography>
            </Box>
            <Box>
              <Typography variant="subtitle2" color="text.secondary">
                Auth0 ID
              </Typography>
              <Typography sx={{ 
                wordBreak: 'break-all',
                fontSize: '0.875rem'
              }}>
                {userInfo.sub}
              </Typography>
            </Box>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}

export default Profile; 