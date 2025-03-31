import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Box, Typography, Button, Avatar, Paper, Divider, Container } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import LogoutButton from './LogoutButton';

function Profile({ userInfo, onLogout, isAdmin }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  const handleAdminClick = () => {
    navigate('/admin');
  };

  if (!userInfo) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h5" gutterBottom>
            Please log in to view your profile
          </Typography>
        </Paper>
      </Container>
    );
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" component="h1">
            Profile
          </Typography>
          <LogoutButton onLogout={onLogout} />
        </Box>
        
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center', 
          mb: 4
        }}>
          {userInfo.picture ? (
            <Avatar
              src={userInfo.picture}
              alt={userInfo.name || userInfo.email}
              sx={{ width: 100, height: 100, mb: 2 }}
            />
          ) : (
            <AccountCircleIcon sx={{ fontSize: 100, color: '#666666', mb: 2 }} />
          )}
          <Typography variant="h4" gutterBottom>
            {userInfo.name || userInfo.email}
          </Typography>
          <Typography color="text.secondary">
            {userInfo.email}
          </Typography>
          <Box sx={{ mt: 2 }}>
            {isAdmin && (
              <Button
                variant="outlined"
                startIcon={<AdminPanelSettingsIcon />}
                onClick={handleAdminClick}
                sx={{ 
                  borderRadius: 0,
                  borderColor: '#1976d2',
                  color: '#1976d2',
                  '&:hover': {
                    borderColor: '#1976d2',
                    backgroundColor: 'rgba(25, 118, 210, 0.04)',
                  }
                }}
              >
                Admin Dashboard
              </Button>
            )}
          </Box>
        </Box>

        <Divider sx={{ my: 4 }} />

        <Box>
          <Typography variant="h6" gutterBottom>
            Profile Information
          </Typography>
          <Typography>
            Email verified: {userInfo.email_verified ? 'Yes' : 'No'}
          </Typography>
          <Typography>
            Last updated: {new Date(userInfo.updated_at).toLocaleString()}
          </Typography>
        </Box>
      </Paper>
    </Container>
  );
}

export default Profile; 