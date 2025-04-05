import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  Divider,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  SecurityOutlined as SecurityIcon,
  CheckCircle as CheckIcon
} from '@mui/icons-material';

const AdminRoles = () => {
  const [roles, setRoles] = useState([]);
  const [permissions, setPermissions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRole, setSelectedRole] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [dialogMode, setDialogMode] = useState('create'); // 'create' or 'edit'
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  
  // Form state
  const [roleName, setRoleName] = useState('');
  const [roleDescription, setRoleDescription] = useState('');
  const [rolePermissions, setRolePermissions] = useState([]);

  useEffect(() => {
    fetchRoles();
    fetchPermissions();
  }, []);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const response = await fetch('http://localhost:5001/api/admin/roles', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch roles');
      }

      const data = await response.json();
      setRoles(data || []);
      setLoading(false);
    } catch (err) {
      console.error('Error fetching roles:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const fetchPermissions = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch('http://localhost:5001/api/admin/permissions', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch permissions');
      }

      const data = await response.json();
      setPermissions(data || []);
    } catch (err) {
      console.error('Error fetching permissions:', err);
      setError(err.message);
    }
  };

  const handleCreateRole = () => {
    setDialogMode('create');
    setRoleName('');
    setRoleDescription('');
    setRolePermissions([]);
    setDialogOpen(true);
  };

  const handleEditRole = (role) => {
    setDialogMode('edit');
    setSelectedRole(role);
    setRoleName(role.name);
    setRoleDescription(role.description || '');
    setRolePermissions(role.permissions?.map(p => p.id) || []);
    setDialogOpen(true);
  };

  const handleDeleteRole = (role) => {
    setSelectedRole(role);
    setDeleteDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedRole(null);
  };

  const handleSaveRole = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const roleData = {
        name: roleName,
        description: roleDescription,
        permission_ids: rolePermissions
      };
      
      if (dialogMode === 'create') {
        // Create new role
        const response = await fetch('http://localhost:5001/api/admin/roles', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(roleData)
        });

        if (!response.ok) {
          throw new Error('Failed to create role');
        }
      } else {
        // Update existing role
        const response = await fetch(`http://localhost:5001/api/admin/roles/${selectedRole.id}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(roleData)
        });

        if (!response.ok) {
          throw new Error('Failed to update role');
        }
      }

      // Refresh roles list
      fetchRoles();
      handleCloseDialog();
    } catch (err) {
      console.error('Error saving role:', err);
      setError(err.message);
    }
  };

  const handleConfirmDelete = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`http://localhost:5001/api/admin/roles/${selectedRole.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to delete role');
      }

      // Remove role from local state
      setRoles(roles.filter(role => role.id !== selectedRole.id));
      setDeleteDialogOpen(false);
      setSelectedRole(null);
    } catch (err) {
      console.error('Error deleting role:', err);
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h5" fontWeight="bold">
          Role Management
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={handleCreateRole}
        >
          Create New Role
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Role Name</TableCell>
                  <TableCell>Description</TableCell>
                  <TableCell>Permissions</TableCell>
                  <TableCell>Users</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {roles.map((role) => (
                  <TableRow key={role.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        <SecurityIcon sx={{ mr: 1, color: 'primary.main' }} />
                        <Typography fontWeight={role.name === 'admin' ? 'bold' : 'normal'}>
                          {role.name}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{role.description || 'No description'}</TableCell>
                    <TableCell>
                      {role.permissions?.length > 0 ? (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                          {role.permissions.map((permission) => (
                            <Chip
                              key={permission.id}
                              label={permission.name}
                              size="small"
                              color="info"
                              variant="outlined"
                              sx={{ mr: 0.5, mb: 0.5 }}
                            />
                          ))}
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No permissions assigned
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      {role.user_count !== undefined ? role.user_count : 'N/A'}
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="Edit role">
                          <IconButton 
                            size="small" 
                            color="primary"
                            onClick={() => handleEditRole(role)}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete role">
                          <IconButton 
                            size="small" 
                            color="error"
                            onClick={() => handleDeleteRole(role)}
                            disabled={role.name === 'admin'} // Prevent deletion of admin role
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
                {roles.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                        No roles found
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </Grid>
      </Grid>

      {/* Create/Edit Role Dialog */}
      <Dialog 
        open={dialogOpen} 
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {dialogMode === 'create' ? 'Create New Role' : `Edit Role: ${selectedRole?.name}`}
        </DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                label="Role Name"
                value={roleName}
                onChange={(e) => setRoleName(e.target.value)}
                fullWidth
                required
                margin="normal"
                disabled={selectedRole?.name === 'admin'} // Prevent renaming of admin role
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                label="Description"
                value={roleDescription}
                onChange={(e) => setRoleDescription(e.target.value)}
                fullWidth
                multiline
                rows={2}
                margin="normal"
              />
            </Grid>
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Permissions
              </Typography>
              <FormControl fullWidth margin="normal">
                <InputLabel>Assign Permissions</InputLabel>
                <Select
                  multiple
                  value={rolePermissions}
                  onChange={(e) => setRolePermissions(e.target.value)}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((permissionId) => {
                        const permission = permissions.find(p => p.id === permissionId);
                        return (
                          <Chip 
                            key={permissionId} 
                            label={permission?.name || permissionId} 
                            color="info"
                          />
                        );
                      })}
                    </Box>
                  )}
                >
                  {permissions.map((permission) => (
                    <MenuItem key={permission.id} value={permission.id}>
                      <Box sx={{ display: 'flex', alignItems: 'center' }}>
                        {rolePermissions.includes(permission.id) && (
                          <CheckIcon fontSize="small" color="success" sx={{ mr: 1 }} />
                        )}
                        <Box>
                          <Typography variant="body1">{permission.name}</Typography>
                          {permission.description && (
                            <Typography variant="caption" color="text.secondary">
                              {permission.description}
                            </Typography>
                          )}
                        </Box>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>
            Cancel
          </Button>
          <Button 
            onClick={handleSaveRole} 
            variant="contained" 
            color="primary"
            disabled={!roleName.trim()} // Disable if name is empty
          >
            {dialogMode === 'create' ? 'Create Role' : 'Save Changes'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Role Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>
          Confirm Delete Role
        </DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete the role <strong>{selectedRole?.name}</strong>?
            This will remove the role from all users who have it assigned.
          </Typography>
          {selectedRole?.user_count > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              This role is currently assigned to {selectedRole.user_count} user(s).
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>
            Cancel
          </Button>
          <Button 
            onClick={handleConfirmDelete} 
            variant="contained" 
            color="error"
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminRoles; 