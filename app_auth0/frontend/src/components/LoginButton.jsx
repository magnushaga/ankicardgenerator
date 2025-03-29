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
            sessionStorage.setItem('access_token', data.tokens.access_token);
            console.log('Stored access token');
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
        window.location.href = data.auth_url;
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