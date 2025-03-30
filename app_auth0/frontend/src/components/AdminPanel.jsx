import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  People as PeopleIcon,
  Security as SecurityIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

const AdminPanel = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalRoles: 0,
    recentAuditLogs: [],
  });

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const token = sessionStorage.getItem('access_token');
        if (!token) {
          throw new Error('No access token found');
        }

        // Fetch users
        const usersResponse = await fetch('http://localhost:5001/api/admin/users', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!usersResponse.ok) {
          throw new Error('Failed to fetch users');
        }

        const usersData = await usersResponse.json();
        setStats(prev => ({
          ...prev,
          totalUsers: usersData.users.length,
          activeUsers: usersData.users.filter(user => user.is_active).length,
        }));

        // Fetch roles
        const rolesResponse = await fetch('http://localhost:5001/api/admin/roles', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!rolesResponse.ok) {
          throw new Error('Failed to fetch roles');
        }

        const rolesData = await rolesResponse.json();
        setStats(prev => ({
          ...prev,
          totalRoles: rolesData.length,
        }));

        // Fetch recent audit logs
        const logsResponse = await fetch('http://localhost:5001/api/admin/audit-logs', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!logsResponse.ok) {
          throw new Error('Failed to fetch audit logs');
        }

        const logsData = await logsResponse.json();
        setStats(prev => ({
          ...prev,
          recentAuditLogs: logsData.logs.slice(0, 5),
        }));

        setLoading(false);
      } catch (err) {
        console.error('Error fetching admin data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchAdminData();
  }, []);

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

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Stats Cards */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <PeopleIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Users</Typography>
              </Box>
              <Typography variant="h4">{stats.totalUsers}</Typography>
              <Typography color="textSecondary">Active Users: {stats.activeUsers}</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <SecurityIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Roles</Typography>
              </Box>
              <Typography variant="h4">{stats.totalRoles}</Typography>
              <Typography color="textSecondary">Total Admin Roles</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <HistoryIcon sx={{ mr: 1 }} />
                <Typography variant="h6">Recent Activity</Typography>
              </Box>
              <Typography variant="h4">{stats.recentAuditLogs.length}</Typography>
              <Typography color="textSecondary">Latest Actions</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Quick Actions */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quick Actions
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<PeopleIcon />}
                  onClick={() => {/* Handle user management */}}
                >
                  Manage Users
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<SecurityIcon />}
                  onClick={() => {/* Handle role management */}}
                >
                  Manage Roles
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<SettingsIcon />}
                  onClick={() => {/* Handle settings */}}
                >
                  Settings
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<AssessmentIcon />}
                  onClick={() => {/* Handle analytics */}}
                >
                  Analytics
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Recent Activity */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List>
              {stats.recentAuditLogs.map((log, index) => (
                <React.Fragment key={log.id}>
                  <ListItem>
                    <ListItemIcon>
                      <HistoryIcon />
                    </ListItemIcon>
                    <ListItemText
                      primary={log.action}
                      secondary={`${new Date(log.created_at).toLocaleString()} - ${log.resource_type}`}
                    />
                  </ListItem>
                  {index < stats.recentAuditLogs.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default AdminPanel; 