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
  Tabs,
  Tab,
  Divider,
  CircularProgress,
  Alert,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  People as PeopleIcon,
  Security as SecurityIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
  School as SchoolIcon,
  MenuBook as MenuBookIcon,
  Dashboard as DashboardIcon,
  Person as PersonIcon,
  AdminPanelSettings as AdminIcon,
} from '@mui/icons-material';
import AdminUsers from './AdminUsers';
import AdminRoles from './AdminRoles';
import AdminAuditLogs from './AdminAuditLogs';
import AdminSettings from './AdminSettings';

function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`admin-tabpanel-${index}`}
      aria-labelledby={`admin-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ py: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AdminPanel = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stats, setStats] = useState({
    totalUsers: 0,
    activeUsers: 0,
    totalRoles: 0,
    totalCourses: 0,
    totalTextbooks: 0,
    recentAuditLogs: [],
  });

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      const token = localStorage.getItem('access_token');
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

      // Fetch courses
      const coursesResponse = await fetch('http://localhost:5001/api/admin/courses/count', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (coursesResponse.ok) {
        const coursesData = await coursesResponse.json();
        setStats(prev => ({
          ...prev,
          totalCourses: coursesData.count || 0,
        }));
      }

      // Fetch textbooks
      const textbooksResponse = await fetch('http://localhost:5001/api/admin/textbooks/count', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (textbooksResponse.ok) {
        const textbooksData = await textbooksResponse.json();
        setStats(prev => ({
          ...prev,
          totalTextbooks: textbooksData.count || 0,
        }));
      }

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

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
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
    <Container maxWidth="lg">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight="bold" sx={{ mb: 1 }}>
          Admin Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Manage users, roles, courses, and system settings
        </Typography>
      </Box>

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab 
            label="Dashboard" 
            icon={<DashboardIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Users" 
            icon={<PeopleIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Roles" 
            icon={<SecurityIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Courses" 
            icon={<SchoolIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Textbooks" 
            icon={<MenuBookIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Activity" 
            icon={<HistoryIcon />} 
            iconPosition="start"
          />
          <Tab 
            label="Settings" 
            icon={<SettingsIcon />} 
            iconPosition="start"
          />
        </Tabs>
      </Box>

      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {/* Stats Cards */}
          <Grid item xs={12} md={4} lg={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PeopleIcon sx={{ mr: 1, color: 'primary.main' }} />
                  <Typography variant="h6">Users</Typography>
                </Box>
                <Typography variant="h3">{stats.totalUsers}</Typography>
                <Typography color="text.secondary">Active Users: {stats.activeUsers}</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4} lg={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <SecurityIcon sx={{ mr: 1, color: 'secondary.main' }} />
                  <Typography variant="h6">Roles</Typography>
                </Box>
                <Typography variant="h3">{stats.totalRoles}</Typography>
                <Typography color="text.secondary">Total Admin Roles</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4} lg={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <SchoolIcon sx={{ mr: 1, color: 'info.main' }} />
                  <Typography variant="h6">Courses</Typography>
                </Box>
                <Typography variant="h3">{stats.totalCourses}</Typography>
                <Typography color="text.secondary">Total Courses</Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4} lg={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <MenuBookIcon sx={{ mr: 1, color: 'warning.main' }} />
                  <Typography variant="h6">Textbooks</Typography>
                </Box>
                <Typography variant="h3">{stats.totalTextbooks}</Typography>
                <Typography color="text.secondary">Total Textbooks</Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12} lg={8}>
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<PersonIcon />}
                    onClick={() => setTabValue(1)}
                    sx={{ justifyContent: 'flex-start', py: 1 }}
                  >
                    Manage Users
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<SecurityIcon />}
                    onClick={() => setTabValue(2)}
                    sx={{ justifyContent: 'flex-start', py: 1 }}
                  >
                    Manage Roles
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<SchoolIcon />}
                    onClick={() => setTabValue(3)}
                    sx={{ justifyContent: 'flex-start', py: 1 }}
                  >
                    Manage Courses
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<MenuBookIcon />}
                    onClick={() => setTabValue(4)}
                    sx={{ justifyContent: 'flex-start', py: 1 }}
                  >
                    Manage Textbooks
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<HistoryIcon />}
                    onClick={() => setTabValue(5)}
                    sx={{ justifyContent: 'flex-start', py: 1 }}
                  >
                    View Activity
                  </Button>
                </Grid>
                <Grid item xs={12} sm={6} md={4}>
                  <Button
                    fullWidth
                    variant="outlined"
                    startIcon={<SettingsIcon />}
                    onClick={() => setTabValue(6)}
                    sx={{ justifyContent: 'flex-start', py: 1 }}
                  >
                    System Settings
                  </Button>
                </Grid>
              </Grid>
            </Paper>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} lg={4}>
            <Paper sx={{ p: 3, height: '100%' }}>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List>
                {stats.recentAuditLogs.length > 0 ? (
                  stats.recentAuditLogs.map((log, index) => (
                    <React.Fragment key={log.id || index}>
                      <ListItem disablePadding sx={{ py: 1 }}>
                        <ListItemIcon sx={{ minWidth: 36 }}>
                          <HistoryIcon fontSize="small" />
                        </ListItemIcon>
                        <ListItemText
                          primary={log.action}
                          secondary={`${new Date(log.created_at).toLocaleString()} - ${log.resource_type || 'System'}`}
                          primaryTypographyProps={{ variant: 'body2', fontWeight: 'medium' }}
                          secondaryTypographyProps={{ variant: 'caption' }}
                        />
                      </ListItem>
                      {index < stats.recentAuditLogs.length - 1 && <Divider component="li" />}
                    </React.Fragment>
                  ))
                ) : (
                  <ListItem>
                    <ListItemText 
                      primary="No recent activity" 
                      primaryTypographyProps={{ color: 'text.secondary' }}
                    />
                  </ListItem>
                )}
              </List>
              {stats.recentAuditLogs.length > 0 && (
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    size="small" 
                    onClick={() => setTabValue(5)}
                    endIcon={<HistoryIcon />}
                  >
                    View All Activity
                  </Button>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <AdminUsers />
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <AdminRoles />
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <Box>
          <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>
            Course Management
          </Typography>
          <Alert severity="info">
            Course management functionality will be implemented in a future update.
          </Alert>
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={4}>
        <Box>
          <Typography variant="h5" fontWeight="bold" sx={{ mb: 3 }}>
            Textbook Management
          </Typography>
          <Alert severity="info">
            Textbook management functionality will be implemented in a future update.
          </Alert>
        </Box>
      </TabPanel>

      <TabPanel value={tabValue} index={5}>
        <AdminAuditLogs />
      </TabPanel>

      <TabPanel value={tabValue} index={6}>
        <AdminSettings />
      </TabPanel>
    </Container>
  );
};

export default AdminPanel; 