import React, { useState, useEffect } from 'react';
import { Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const LoginButton = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if we're handling the Auth0 callback
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');
      
      if (code) {
        try {
          setIsLoading(true);
          console.log('Received Auth0 code, exchanging for tokens...');
          
          const response = await fetch('http://localhost:5001/callback', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
          });

          if (!response.ok) {
            const errorData = await response.json();
            console.error('Token exchange failed:', errorData);
            throw new Error(errorData.error || 'Failed to exchange code for tokens');
          }

          const data = await response.json();
          console.log('Received tokens and user info:', {
            hasAccessToken: !!data.tokens?.access_token,
            hasUserInfo: !!data.user
          });

          // Store tokens and user info
          if (data.tokens?.access_token) {
            localStorage.setItem('access_token', data.tokens.access_token);
            localStorage.setItem('tokens', JSON.stringify(data.tokens));
            console.log('Stored access token in localStorage');
          }
          
          if (data.user) {
            localStorage.setItem('user_info', JSON.stringify(data.user));
            console.log('Stored user info:', data.user);
          }

          // Redirect to the saved return URL or home
          const returnTo = localStorage.getItem('returnTo') || '/';
          localStorage.removeItem('returnTo');
          navigate(returnTo);
        } catch (err) {
          console.error('Error handling callback:', err);
          setError(err.message);
        } finally {
          setIsLoading(false);
        }
      }
    };

    handleCallback();
  }, [navigate]);

  const handleLogin = async () => {
    try {
      setIsLoading(true);
      setError(null);
      console.log('Starting login process...');

      // Check for existing access token
      const existingToken = localStorage.getItem('access_token');
      if (existingToken) {
        console.log('Found existing access token, attempting to get user info...');
        try {
          const response = await fetch('http://localhost:5001/userinfo', {
            headers: {
              'Authorization': `Bearer ${existingToken}`,
              'Content-Type': 'application/json'
            }
          });

          if (response.ok) {
            const data = await response.json();
            console.log('Successfully retrieved user info with existing token');
            
            // Store user info if not already present
            if (data.user && !localStorage.getItem('user_info')) {
              localStorage.setItem('user_info', JSON.stringify(data.user));
            }
            
            // Redirect to saved return URL or home
            const returnTo = localStorage.getItem('returnTo') || '/';
            localStorage.removeItem('returnTo');
            navigate(returnTo);
            return;
          } else {
            console.log('Existing token invalid, clearing storage and proceeding with new login');
            localStorage.clear();
          }
        } catch (err) {
          console.error('Error verifying existing token:', err);
          localStorage.clear();
        }
      }
      
      // If we get here, either no token exists or it's invalid
      // Clear any existing auth data
      localStorage.clear();
      sessionStorage.clear();
      
      const response = await fetch("http://localhost:5001/login");
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to get login URL');
      }
      
      const data = await response.json();
      console.log('Received auth URL:', data.auth_url);
      
      if (data.auth_url) {
        // Store the current URL to redirect back after login
        localStorage.setItem('returnTo', window.location.pathname);
        
        // Add prompt=login to force re-authentication
        const loginUrl = new URL(data.auth_url);
        loginUrl.searchParams.set('prompt', 'login');
        loginUrl.searchParams.set('response_type', 'code');
        loginUrl.searchParams.set('scope', 'openid profile email');
        
        window.location.href = loginUrl.toString();
      } else {
        throw new Error('No auth URL received');
      }
    } catch (error) {
      console.error("Login error:", error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant="outlined"
      onClick={handleLogin}
      disabled={isLoading}
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
      {isLoading ? 'Logging in...' : 'Login'}
    </Button>
  );
};

export default LoginButton; 