import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, TextField, Avatar, Menu, MenuItem, IconButton } from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import { useNavigate, useLocation } from 'react-router-dom';
import LoginButton from './LoginButton';
import LogoutButton from './LogoutButton';
import SearchIcon from '@mui/icons-material/Search';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';

const Header = ({ onSearch, searchQuery, setSearchQuery, userInfo, tokens, onLogout }) => {
  const [error, setError] = useState(null);
  const [anchorEl, setAnchorEl] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
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

  const handleAdminClick = async () => {
    handleMenuClose();
    const token = sessionStorage.getItem('access_token');
    if (!token) {
      navigate('/');
      return;
    }

    try {
      const response = await fetch('http://localhost:5001/api/admin/check', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        setIsAdmin(true);
        navigate('/admin');
      } else {
        setIsAdmin(false);
        // Optionally show an error message or redirect
        navigate('/');
      }
    } catch (error) {
      console.error('Error checking admin status:', error);
      setIsAdmin(false);
      navigate('/');
    }
  };

  const handleLogoutClick = () => {
    handleMenuClose();
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
          size="small"
          placeholder="Search decks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && onSearch()}
          sx={{
            '& .MuiOutlinedInput-root': {
              '& fieldset': {
                borderColor: '#e0e0e0',
              },
              '&:hover fieldset': {
                borderColor: '#bdbdbd',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#1976d2',
              },
              bgcolor: '#f5f5f5',
              borderRadius: '8px',
            },
          }}
        />
        <Button
          variant="outlined"
          onClick={onSearch}
          sx={{ 
            minWidth: 'auto',
            p: 1,
            borderColor: '#e0e0e0',
            color: '#666666',
            '&:hover': {
              borderColor: '#bdbdbd',
              bgcolor: '#f5f5f5',
            }
          }}
        >
          <SearchIcon />
        </Button>
      </Box>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        {userInfo ? (
          <>
            {isAdmin && (
              <IconButton
                color="inherit"
                onClick={() => navigate('/admin')}
                title="Admin Dashboard"
              >
                <AdminPanelSettingsIcon />
              </IconButton>
            )}
            <IconButton
              onClick={handleMenuOpen}
              sx={{ 
                p: 1,
                '&:hover': {
                  bgcolor: 'rgba(0, 0, 0, 0.04)',
                }
              }}
            >
              {userInfo.picture ? (
                <Avatar
                  src={userInfo.picture}
                  alt={userInfo.name || userInfo.email}
                  sx={{ width: 32, height: 32 }}
                />
              ) : (
                <AccountCircleIcon sx={{ fontSize: 32, color: '#666666' }} />
              )}
            </IconButton>
            <Menu
              anchorEl={anchorEl}
              open={Boolean(anchorEl)}
              onClose={handleMenuClose}
              PaperProps={{
                sx: {
                  mt: 1,
                  minWidth: 200,
                  borderRadius: 0,
                  boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                }
              }}
            >
              <MenuItem onClick={handleProfileClick}>
                <PersonIcon sx={{ mr: 1, fontSize: 20 }} />
                Profile
              </MenuItem>
              {isAdmin && (
                <MenuItem onClick={handleAdminClick}>
                  <AdminPanelSettingsIcon sx={{ mr: 1, fontSize: 20 }} />
                  Admin Dashboard
                </MenuItem>
              )}
              <MenuItem onClick={handleLogoutClick}>
                <LogoutIcon sx={{ mr: 1, fontSize: 20 }} />
                Logout
              </MenuItem>
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