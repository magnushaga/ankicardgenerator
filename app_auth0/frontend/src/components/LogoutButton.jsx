import React, { useState } from 'react';
import { MenuItem } from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';

const LogoutButton = ({ onLogout }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogout = async () => {
    try {
      setIsLoading(true);
      setError(null);

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

      // Clear local data
      onLogout();

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

  return (
    <MenuItem onClick={handleLogout} disabled={isLoading}>
      <LogoutIcon sx={{ mr: 1 }} /> {isLoading ? 'Logging out...' : 'Logout'}
    </MenuItem>
  );
};

export default LogoutButton; 