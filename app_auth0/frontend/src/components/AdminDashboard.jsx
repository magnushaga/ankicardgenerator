import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, CircularProgress, Alert } from '@mui/material';
import AdminPanel from './AdminPanel';

const AdminDashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [hasAccess, setHasAccess] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const checkAdminAccess = async () => {
      try {
        const token = sessionStorage.getItem('access_token');
        if (!token) {
          console.log('No access token found');
          navigate('/');
          return;
        }

        console.log('Checking admin access with token:', token.substring(0, 20) + '...');
        const response = await fetch('http://localhost:5001/api/admin/check', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        console.log('Admin check response status:', response.status);
        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.message || 'Failed to verify admin access');
        }

        setHasAccess(true);
        setLoading(false);
      } catch (err) {
        console.error('Error checking admin access:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    checkAdminAccess();
  }, [navigate]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!hasAccess) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="warning">You do not have permission to access the admin dashboard.</Alert>
      </Box>
    );
  }

  return <AdminPanel />;
};

export default AdminDashboard; 