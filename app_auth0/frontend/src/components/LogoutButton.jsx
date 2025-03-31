import React, { useState } from 'react';
import { Button } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';

const LogoutButton = ({ onLogout }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      
      // Get the current URL to return to after logout
      const returnTo = window.location.origin;
      
      // Call the backend logout endpoint
      const response = await fetch('http://localhost:5001/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ returnTo }),
      });

      if (!response.ok) {
        throw new Error('Logout failed');
      }

      const data = await response.json();
      
      // Clear local storage
      localStorage.clear();
      
      // Redirect to Auth0 logout URL with federated logout and force re-authentication
      const logoutUrl = new URL(data.logout_url);
      logoutUrl.searchParams.set('federated', 'true');
      logoutUrl.searchParams.set('client_id', process.env.REACT_APP_AUTH0_CLIENT_ID);
      logoutUrl.searchParams.set('returnTo', returnTo);
      logoutUrl.searchParams.set('prompt', 'login'); // Force re-authentication
      
      // Force a complete logout by redirecting to Auth0
      window.location.href = logoutUrl.toString();
      
    } catch (error) {
      console.error('Logout error:', error);
      // If there's an error, still try to clear local data and redirect to home
      localStorage.clear();
      window.location.href = '/';
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant="outlined"
      color="error"
      startIcon={<LogoutIcon />}
      onClick={handleLogout}
      disabled={isLoading}
      sx={{ 
        borderRadius: 0,
        borderColor: '#d32f2f',
        color: '#d32f2f',
        '&:hover': {
          borderColor: '#d32f2f',
          backgroundColor: 'rgba(211, 47, 47, 0.04)',
        }
      }}
    >
      {isLoading ? 'Logging out...' : 'Logout'}
    </Button>
  );
};

export default LogoutButton; 