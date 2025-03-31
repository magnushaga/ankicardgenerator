import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  IconButton,
  Alert,
  CircularProgress,
  Grid,
  Card,
  CardContent,
  Tooltip,
  Chip,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import PersonIcon from '@mui/icons-material/Person';
import SecurityIcon from '@mui/icons-material/Security';
import HistoryIcon from '@mui/icons-material/History';
import {
  People as PeopleIcon,
  MenuBook as MenuBookIcon,
  Analytics as AnalyticsIcon,
  Report as ReportIcon,
  Visibility as VisibilityIcon,
  Block as BlockIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
} from '@mui/icons-material';

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
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

const AdminDashboard = () => {
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [users, setUsers] = useState([]);
  const [decks, setDecks] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [reports, setReports] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [selectedDeck, setSelectedDeck] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogType, setDialogType] = useState(null);

  const fetchData = async (endpoint, options = {}) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/admin/${endpoint}`, {
        ...options,
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch data');
      }

      return await response.json();
    } catch (err) {
      console.error(`Error fetching ${endpoint}:`, err);
      setError(err.message);
      return null;
    }
  };

  const loadUsers = async () => {
    setLoading(true);
    const data = await fetchData('users');
    if (data) {
      setUsers(data.users);
    }
    setLoading(false);
  };

  const loadDecks = async () => {
    setLoading(true);
    const data = await fetchData('decks');
    if (data) {
      setDecks(data.decks);
    }
    setLoading(false);
  };

  const loadAnalytics = async () => {
    setLoading(true);
    const [systemData, activityData] = await Promise.all([
      fetchData('analytics/system'),
      fetchData('analytics/activity'),
    ]);
    if (systemData && activityData) {
      setAnalytics({ system: systemData, activity: activityData });
    }
    setLoading(false);
  };

  const loadReports = async () => {
    setLoading(true);
    const data = await fetchData('content/reports');
    if (data) {
      setReports(data.reports);
    }
    setLoading(false);
  };

  useEffect(() => {
    switch (tabValue) {
      case 0:
        loadUsers();
        break;
      case 1:
        loadDecks();
        break;
      case 2:
        loadAnalytics();
        break;
      case 3:
        loadReports();
        break;
      default:
        break;
    }
  }, [tabValue]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleUserStatusChange = async (userId, isActive) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/admin/users/${userId}/status`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_active: isActive }),
      });

      if (!response.ok) {
        throw new Error('Failed to update user status');
      }

      loadUsers();
    } catch (err) {
      console.error('Error updating user status:', err);
      setError(err.message);
    }
  };

  const handleDeckVisibilityChange = async (deckId, isPublic) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/admin/decks/${deckId}/visibility`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_public: isPublic }),
      });

      if (!response.ok) {
        throw new Error('Failed to update deck visibility');
      }

      loadDecks();
    } catch (err) {
      console.error('Error updating deck visibility:', err);
      setError(err.message);
    }
  };

  const handleReportResolution = async (reportId, status) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:5001/api/admin/content/reports/${reportId}/resolve`, {
        method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
            },
        body: JSON.stringify({ status }),
          });

      if (!response.ok) {
        throw new Error('Failed to resolve report');
      }

      loadReports();
      } catch (err) {
      console.error('Error resolving report:', err);
        setError(err.message);
    }
  };

  const renderUsersTab = () => (
    <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
            <TableCell>User</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
              <TableCell>{user.username || user.email.split('@')[0]}</TableCell>
                    <TableCell>{user.email}</TableCell>
              <TableCell>
                <Chip
                  label={user.is_active ? 'Active' : 'Suspended'}
                  color={user.is_active ? 'success' : 'error'}
                />
              </TableCell>
                    <TableCell>
                <Tooltip title={user.is_active ? 'Suspend User' : 'Activate User'}>
                  <IconButton
                    onClick={() => handleUserStatusChange(user.id, !user.is_active)}
                    color={user.is_active ? 'error' : 'success'}
                  >
                    {user.is_active ? <BlockIcon /> : <CheckCircleIcon />}
                      </IconButton>
                </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
  );

  const renderDecksTab = () => (
    <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
            <TableCell>Title</TableCell>
            <TableCell>Owner</TableCell>
            <TableCell>Visibility</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
          {decks.map((deck) => (
            <TableRow key={deck.id}>
              <TableCell>{deck.title}</TableCell>
              <TableCell>{deck.user_id}</TableCell>
              <TableCell>
                <Chip
                  label={deck.is_public ? 'Public' : 'Private'}
                  color={deck.is_public ? 'success' : 'default'}
                />
              </TableCell>
                    <TableCell>
                <Tooltip title={deck.is_public ? 'Make Private' : 'Make Public'}>
                  <IconButton
                    onClick={() => handleDeckVisibilityChange(deck.id, !deck.is_public)}
                    color={deck.is_public ? 'default' : 'success'}
                  >
                    <VisibilityIcon />
                      </IconButton>
                </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
  );

  const renderAnalyticsTab = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6">System Overview</Typography>
            {analytics?.system && (
              <>
                <Typography>Total Users: {analytics.system.total_users}</Typography>
                <Typography>Total Decks: {analytics.system.total_decks}</Typography>
                <Typography>Total Sessions: {analytics.system.total_sessions}</Typography>
              </>
            )}
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6">Activity Metrics</Typography>
            {analytics?.activity && (
              <>
                <Typography>Daily Active Users: {analytics.activity.daily_active_users}</Typography>
                <Typography>
                  Avg Session Duration: {Math.round(analytics.activity.average_session_duration / 60)} minutes
                </Typography>
              </>
            )}
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6">Recent Activity</Typography>
            {analytics?.system?.recent_users && (
              <Typography>
                New Users Today: {analytics.system.recent_users.length}
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderReportsTab = () => (
    <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
            <TableCell>Report ID</TableCell>
            <TableCell>Type</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
          {reports.map((report) => (
            <TableRow key={report.id}>
              <TableCell>{report.id}</TableCell>
              <TableCell>{report.content_type}</TableCell>
              <TableCell>
                <Chip
                  label={report.status}
                  color={report.status === 'pending' ? 'warning' : 'success'}
                />
              </TableCell>
              <TableCell>
                {report.status === 'pending' && (
                  <>
                    <Tooltip title="Approve">
                      <IconButton
                        onClick={() => handleReportResolution(report.id, 'approved')}
                        color="success"
                      >
                        <CheckCircleIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Reject">
                      <IconButton
                        onClick={() => handleReportResolution(report.id, 'rejected')}
                        color="error"
                      >
                        <CancelIcon />
                      </IconButton>
                    </Tooltip>
                  </>
                )}
              </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
  );

  return (
    <Box sx={{ width: '100%', p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Admin Dashboard
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab icon={<PeopleIcon />} label="Users" />
          <Tab icon={<MenuBookIcon />} label="Decks" />
          <Tab icon={<AnalyticsIcon />} label="Analytics" />
          <Tab icon={<ReportIcon />} label="Reports" />
        </Tabs>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : (
        <>
          <TabPanel value={tabValue} index={0}>
            {renderUsersTab()}
          </TabPanel>
          <TabPanel value={tabValue} index={1}>
            {renderDecksTab()}
          </TabPanel>
          <TabPanel value={tabValue} index={2}>
            {renderAnalyticsTab()}
          </TabPanel>
          <TabPanel value={tabValue} index={3}>
            {renderReportsTab()}
          </TabPanel>
            </>
          )}
      </Box>
    );
};

export default AdminDashboard; 