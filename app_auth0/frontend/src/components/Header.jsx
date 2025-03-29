import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, TextField, Avatar, Menu } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { useNavigate, useLocation } from 'react-router-dom';
import LoginButton from './LoginButton';
import LogoutButton from './LogoutButton';

const Header = ({ onSearch, searchQuery, setSearchQuery, userInfo, tokens, onLogout }) => {
  const [error, setError] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get("code");
    const error = urlParams.get("error");
    const errorDescription = urlParams.get("error_description");

    if (error) {
      console.error('Auth0 error:', error, errorDescription);
      setError(`Authentication error: ${errorDescription || error}`);
      // Clean up the URL
      navigate('/', { replace: true });
      return;
    }

    if (code) {
      console.log('Received Auth0 code:', code);
      // Only exchange code if we haven't already processed it
      const processedCode = sessionStorage.getItem("processed_code");
      if (code !== processedCode) {
        sessionStorage.setItem("processed_code", code);
        exchangeCodeForToken(code);
      }
      // Clean up the URL after processing the code
      navigate('/', { replace: true });
    }
  }, [location, navigate]);

  const exchangeCodeForToken = async (code) => {
    try {
      console.log('Exchanging code for token...');
      setError(null);
      
      const response = await fetch('http://localhost:5001/callback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          redirect_uri: 'http://localhost:5173',
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to exchange code for token');
      }

      const data = await response.json();
      console.log('Received tokens and user info from backend');
      
      // Store tokens and user info
      sessionStorage.setItem('access_token', data.tokens.access_token);
      sessionStorage.setItem('id_token', data.tokens.id_token);
      localStorage.setItem('user_info', JSON.stringify(data.user));
      localStorage.setItem('tokens', JSON.stringify(data.tokens));
      
      // Reload the page to update the state
      window.location.reload();
      
    } catch (error) {
      console.error('Token exchange error:', error);
      setError(error.message);
      onLogout();
    }
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleProfileClick = () => {
    handleMenuClose();
    navigate('/profile', { replace: true });
  };

  return (
    <Box sx={{ 
      width: '100%',
      p: 2,
      borderBottom: '1px solid #e0e0e0',
      backgroundColor: '#ffffff'
    }}>
      <Box sx={{ 
        maxWidth: 1000, 
        margin: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          mb: 2
        }}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: 1
          }}>
            <MenuBookIcon sx={{ color: '#000000' }} />
            <Typography variant="h4" sx={{ 
              fontWeight: 300,
              letterSpacing: 1,
              color: '#000000'
            }}>
              Anki Card Generator
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {userInfo ? (
              <>
                <Button
                  variant="outlined"
                  onClick={handleProfileClick}
                  sx={{ 
                    py: 1,
                    px: 2,
                    borderRadius: 0,
                    textTransform: 'none',
                    borderColor: '#000000',
                    color: '#000000',
                    '&:hover': {
                      borderColor: '#000000',
                      backgroundColor: 'rgba(0, 0, 0, 0.04)'
                    }
                  }}
                >
                  Profile
                </Button>
                <Box sx={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  gap: 1,
                  cursor: 'pointer'
                }} onClick={handleMenuOpen}>
                  {userInfo.picture ? (
                    <Avatar 
                      src={userInfo.picture} 
                      alt={userInfo.name}
                      sx={{ width: 32, height: 32 }}
                    />
                  ) : (
                    <AccountCircleIcon sx={{ fontSize: 32, color: '#000000' }} />
                  )}
                  <Typography sx={{ color: '#000000' }}>
                    {userInfo.name}
                  </Typography>
                </Box>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleMenuClose}
                >
                  <LogoutButton onLogout={onLogout} />
                </Menu>
              </>
            ) : (
              <LoginButton />
            )}
          </Box>
        </Box>

        <Box sx={{ 
          display: 'flex', 
          gap: 2,
          alignItems: 'center'
        }}>
          <TextField
            fullWidth
            label="Search decks by title"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && onSearch()}
            sx={{ 
              '& .MuiOutlinedInput-root': {
                borderRadius: 0,
                borderColor: '#000000'
              },
              '& .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline': {
                borderColor: '#000000'
              },
              '& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline': {
                borderColor: '#000000'
              },
              '& .MuiInputLabel-root.Mui-focused': {
                color: '#000000'
              }
            }}
          />
          <Button
            variant="outlined"
            onClick={onSearch}
            sx={{ 
              py: 1.5,
              px: 3,
              borderRadius: 0,
              textTransform: 'none',
              fontSize: '1.1rem',
              borderColor: '#000000',
              color: '#000000',
              '&:hover': {
                borderColor: '#000000',
                backgroundColor: 'rgba(0, 0, 0, 0.04)'
              }
            }}
          >
            Search
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default Header; 