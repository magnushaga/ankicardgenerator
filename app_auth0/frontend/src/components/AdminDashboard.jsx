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
  CircularProgress
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import PersonIcon from '@mui/icons-material/Person';
import SecurityIcon from '@mui/icons-material/Security';
import HistoryIcon from '@mui/icons-material/History';

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

function AdminDashboard() {
  const [tabValue, setTabValue] = useState(0);
  const [users, setUsers] = useState([]);
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState('');
  const [selectedItem, setSelectedItem] = useState(null);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    fetchAdminData();
  }, []);

  const fetchAdminData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      if (!token) throw new Error('No access token found');

      // Fetch users
      const usersResponse = await fetch('http://localhost:5001/api/admin/users', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!usersResponse.ok) throw new Error('Failed to fetch users');
      const usersData = await usersResponse.json();
      setUsers(usersData.users);

      // Fetch roles
      const rolesResponse = await fetch('http://localhost:5001/api/admin/roles', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!rolesResponse.ok) throw new Error('Failed to fetch roles');
      const rolesData = await rolesResponse.json();
      setRoles(rolesData);

      // Fetch permissions
      const permissionsResponse = await fetch('http://localhost:5001/api/admin/permissions', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!permissionsResponse.ok) throw new Error('Failed to fetch permissions');
      const permissionsData = await permissionsResponse.json();
      setPermissions(permissionsData);

      // Fetch audit logs
      const logsResponse = await fetch('http://localhost:5001/api/admin/audit-logs', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (!logsResponse.ok) throw new Error('Failed to fetch audit logs');
      const logsData = await logsResponse.json();
      setAuditLogs(logsData.logs);

    } catch (err) {
      setError(err.message);
      console.error('Error fetching admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (type, item = null) => {
    setDialogType(type);
    setSelectedItem(item);
    setFormData(item || {});
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedItem(null);
    setFormData({});
  };

  const handleFormChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async () => {
    try {
      const token = localStorage.getItem('access_token');
      let response;

      switch (dialogType) {
        case 'editUser':
          response = await fetch(`http://localhost:5001/api/admin/users/${selectedItem.id}`, {
            method: 'PUT',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
          });
          break;
        case 'createRole':
          response = await fetch('http://localhost:5001/api/admin/roles', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
          });
          break;
        // Add more cases for other operations
      }

      if (!response.ok) throw new Error('Operation failed');
      
      handleCloseDialog();
      fetchAdminData(); // Refresh data
    } catch (err) {
      setError(err.message);
      console.error('Error performing operation:', err);
    }
  };

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
      <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Admin Dashboard
      </Typography>

      <Paper sx={{ width: '100%' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<PersonIcon />} label="Users" />
          <Tab icon={<SecurityIcon />} label="Roles" />
          <Tab icon={<HistoryIcon />} label="Audit Logs" />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog('createUser')}
            >
              Add User
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Email</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>{user.is_active ? 'Active' : 'Inactive'}</TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleOpenDialog('editUser', user)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton color="error">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Box sx={{ mb: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => handleOpenDialog('createRole')}
            >
              Add Role
            </Button>
          </Box>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {roles.map((role) => (
                  <TableRow key={role.id}>
                    <TableCell>{role.name}</TableCell>
                    <TableCell>{role.description}</TableCell>
                    <TableCell>
                      <IconButton onClick={() => handleOpenDialog('editRole', role)}>
                        <EditIcon />
                      </IconButton>
                      <IconButton color="error">
                        <DeleteIcon />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Admin</TableCell>
                  <TableCell>Action</TableCell>
                  <TableCell>Resource</TableCell>
                  <TableCell>Date</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {auditLogs.map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>{log.admin_id}</TableCell>
                    <TableCell>{log.action}</TableCell>
                    <TableCell>{log.resource_type}</TableCell>
                    <TableCell>{new Date(log.created_at).toLocaleString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>

      {/* Dialog for creating/editing items */}
      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>
          {dialogType === 'createUser' ? 'Create New User' :
           dialogType === 'editUser' ? 'Edit User' :
           dialogType === 'createRole' ? 'Create New Role' :
           dialogType === 'editRole' ? 'Edit Role' : 'Action'}
        </DialogTitle>
        <DialogContent>
          {dialogType.includes('User') && (
            <>
              <TextField
                autoFocus
                margin="dense"
                name="name"
                label="Name"
                fullWidth
                value={formData.name || ''}
                onChange={handleFormChange}
              />
              <TextField
                margin="dense"
                name="email"
                label="Email"
                type="email"
                fullWidth
                value={formData.email || ''}
                onChange={handleFormChange}
              />
            </>
          )}
          {dialogType.includes('Role') && (
            <>
              <TextField
                autoFocus
                margin="dense"
                name="name"
                label="Role Name"
                fullWidth
                value={formData.name || ''}
                onChange={handleFormChange}
              />
              <TextField
                margin="dense"
                name="description"
                label="Description"
                fullWidth
                multiline
                rows={3}
                value={formData.description || ''}
                onChange={handleFormChange}
              />
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {dialogType.startsWith('create') ? 'Create' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>
      </Box>
    );
  }

export default AdminDashboard; 