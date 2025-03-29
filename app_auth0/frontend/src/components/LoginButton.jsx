import React, { useState } from 'react';
import { Button } from '@mui/material';

const LoginButton = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

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