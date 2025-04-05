import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  TextField,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  useTheme,
  useMediaQuery,
  Button,
  Badge,
  InputAdornment
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTheme as useCustomTheme } from '../lib/ThemeContext';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import LogoutIcon from '@mui/icons-material/Logout';
import PersonIcon from '@mui/icons-material/Person';
import LoginButton from './LoginButton';
import LogoutButton from './LogoutButton';
import SearchIcon from '@mui/icons-material/Search';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import NotificationsIcon from '@mui/icons-material/Notifications';

const Header = ({ onSearch, searchQuery, setSearchQuery, userInfo, tokens, onLogout, isAdmin, onLoginSuccess }) => {
  const [anchorEl, setAnchorEl] = useState(null);
  const theme = useTheme();
  const { isDarkMode, toggleTheme } = useCustomTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [error, setError] = useState(null);
  const [isProcessingCode, setIsProcessingCode] = useState(false);
  const [lastTokenVerification, setLastTokenVerification] = useState(null);
  const TOKEN_VERIFICATION_INTERVAL = 5 * 60 * 1000; // 5 minutes in milliseconds

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
        
        if (typeof onLoginSuccess === 'function') {
          await new Promise(resolve => {
            onLoginSuccess(data.user, data.tokens);
            setTimeout(resolve, 100);
          });
        }

        processedCodes.push(code);
        localStorage.setItem('processed_codes', JSON.stringify(processedCodes));
      }
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
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider'
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Left side - Logo and Navigation */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Box 
            sx={{ 
              display: 'flex', 
              alignItems: 'center',
              pl: 2
            }}
          >
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ 
                fontWeight: 700,
                background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                backgroundClip: 'text',
                textFillColor: 'transparent',
                mr: 2,
                cursor: 'pointer'
              }}
              onClick={() => navigate('/')}
            >
              StudIQ
            </Typography>
          </Box>
          <Box sx={{ display: { xs: 'none', md: 'flex' }, gap: 1 }}>
            {['Courses', 'Textbooks', 'Universities', 'Pricing'].map((item) => (
              <Button 
                key={item} 
                color="inherit" 
                onClick={() => navigate(`/${item.toLowerCase()}`)}
                sx={{ 
                  textTransform: 'none',
                  color: 'text.primary',
                  '&:hover': {
                    color: theme.palette.primary.main,
                    bgcolor: 'transparent'
                  }
                }}
              >
                {item}
              </Button>
            ))}
          </Box>
        </Box>

        {/* Center - Search (only show if user is logged in) */}
        {userInfo && (
          <Box sx={{ flex: 1, maxWidth: 400, mx: 4, display: { xs: 'none', md: 'block' } }}>
            <TextField
              fullWidth
              size="small"
              placeholder="Search decks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && onSearch()}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon color="action" />
                  </InputAdornment>
                ),
              }}
              sx={{
                '& .MuiOutlinedInput-root': {
                  bgcolor: 'background.default',
                  '& fieldset': {
                    borderColor: 'divider'
                  },
                  '&:hover fieldset': {
                    borderColor: 'primary.main'
                  }
                }
              }}
            />
          </Box>
        )}

        {/* Right side - Theme toggle, Notifications, Admin button, and User menu */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <IconButton 
            onClick={toggleTheme} 
            color="inherit"
            sx={{ color: 'text.primary' }}
          >
            {isDarkMode ? <Brightness7Icon /> : <Brightness4Icon />}
          </IconButton>

          {/* Notifications */}
          {userInfo && (
            <IconButton 
              color="inherit"
              sx={{ color: 'text.primary' }}
            >
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
          )}

          {/* Admin Dashboard Button - Only show if user is admin */}
          {userInfo && isAdmin && (
            <Button
              variant="outlined"
              size="small"
              startIcon={<AdminPanelSettingsIcon />}
              onClick={() => navigate('/admin')}
              sx={{ 
                mr: 1,
                color: 'primary.main',
                borderColor: 'primary.main',
                '&:hover': {
                  borderColor: 'primary.dark',
                  bgcolor: 'primary.light',
                  color: 'primary.dark'
                }
              }}
            >
              Admin
            </Button>
          )}

          {userInfo ? (
            <>
              <IconButton
                onClick={handleMenu}
                sx={{ color: 'text.primary' }}
              >
                <Avatar 
                  src={userInfo.picture} 
                  alt={userInfo.name}
                  sx={{ width: 32, height: 32 }}
                >
                  {!userInfo.picture && <AccountCircleIcon />}
                </Avatar>
              </IconButton>
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={handleClose}
                PaperProps={{
                  sx: {
                    mt: 1.5,
                    minWidth: 200,
                    boxShadow: theme.shadows[3]
                  }
                }}
              >
                <MenuItem onClick={handleProfile}>
                  <PersonIcon sx={{ mr: 1 }} /> Profile
                </MenuItem>
                {isAdmin && (
                  <MenuItem onClick={handleAdminPanel}>
                    <AdminPanelSettingsIcon sx={{ mr: 1 }} /> Admin Dashboard
                  </MenuItem>
                )}
                <MenuItem onClick={handleLogout}>
                  <LogoutIcon sx={{ mr: 1 }} /> Logout
                </MenuItem>
              </Menu>
            </>
          ) : (
            <LoginButton />
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Header; 