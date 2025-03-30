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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import ClearAllIcon from '@mui/icons-material/ClearAll';

const AdminPermissions = ({ userInfo, accessToken }) => {
  const [permissions, setPermissions] = useState({ user_permissions: {}, resource_owners: {} });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [openAddDialog, setOpenAddDialog] = useState(false);
  const [openOwnerDialog, setOpenOwnerDialog] = useState(false);
  const [newPermission, setNewPermission] = useState({
    user_id: '',
    resource_type: '',
    resource_id: '',
    permission: '',
  });
  const [newOwner, setNewOwner] = useState({
    user_id: '',
    resource_type: '',
    resource_id: '',
  });

  // Available permissions and resource types
  const availablePermissions = [
    'read', 'write', 'delete', 'share', 'admin',
    'create_live_deck', 'edit_live_deck', 'use_ai_features',
    'use_media', 'use_analytics', 'use_export',
    'use_import', 'use_api', 'use_priority_support'
  ];

  const resourceTypes = [
    'deck', 'live_deck', 'part', 'chapter',
    'topic', 'card', 'study_session', 'user'
  ];

  useEffect(() => {
    fetchPermissions();
  }, []);

  const fetchPermissions = async () => {
    try {
      const response = await fetch('http://localhost:5002/api/admin/permissions', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) throw new Error('Failed to fetch permissions');
      const data = await response.json();
      setPermissions(data);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleAddPermission = async () => {
    try {
      const response = await fetch('http://localhost:5002/api/admin/permissions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPermission),
      });
      if (!response.ok) throw new Error('Failed to add permission');
      setSuccess('Permission added successfully');
      setOpenAddDialog(false);
      setNewPermission({ user_id: '', resource_type: '', resource_id: '', permission: '' });
      fetchPermissions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleSetOwner = async () => {
    try {
      const response = await fetch('http://localhost:5002/api/admin/permissions/owner', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newOwner),
      });
      if (!response.ok) throw new Error('Failed to set resource owner');
      setSuccess('Resource owner set successfully');
      setOpenOwnerDialog(false);
      setNewOwner({ user_id: '', resource_type: '', resource_id: '' });
      fetchPermissions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRemovePermission = async (user_id, resource_type, resource_id, permission) => {
    try {
      const response = await fetch('http://localhost:5002/api/admin/permissions', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id,
          resource_type,
          resource_id,
          permission,
        }),
      });
      if (!response.ok) throw new Error('Failed to remove permission');
      setSuccess('Permission removed successfully');
      fetchPermissions();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleClearPermissions = async () => {
    if (!window.confirm('Are you sure you want to clear all permissions?')) return;
    
    try {
      const response = await fetch('http://localhost:5002/api/admin/permissions/clear', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) throw new Error('Failed to clear permissions');
      setSuccess('All permissions cleared successfully');
      fetchPermissions();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h4">Permission Management</Typography>
        <Box>
          <Tooltip title="Add Permission">
            <IconButton onClick={() => setOpenAddDialog(true)} color="primary">
              <AddIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Set Resource Owner">
            <IconButton onClick={() => setOpenOwnerDialog(true)} color="primary">
              <PersonAddIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Clear All Permissions">
            <IconButton onClick={handleClearPermissions} color="error">
              <ClearAllIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>User ID</TableCell>
              <TableCell>Resource Type</TableCell>
              <TableCell>Resource ID</TableCell>
              <TableCell>Permissions</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {Object.entries(permissions.user_permissions).map(([user_id, userResources]) =>
              Object.entries(userResources).map(([resourceKey, perms]) => {
                const [resource_type, resource_id] = resourceKey.split(':');
                return (
                  <TableRow key={`${user_id}-${resourceKey}`}>
                    <TableCell>{user_id}</TableCell>
                    <TableCell>{resource_type}</TableCell>
                    <TableCell>{resource_id}</TableCell>
                    <TableCell>
                      {perms.map(perm => (
                        <span key={perm} style={{ marginRight: '8px' }}>
                          {perm}
                        </span>
                      ))}
                    </TableCell>
                    <TableCell>
                      {perms.map(perm => (
                        <Tooltip key={perm} title="Remove Permission">
                          <IconButton
                            size="small"
                            onClick={() => handleRemovePermission(user_id, resource_type, resource_id, perm)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      ))}
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add Permission Dialog */}
      <Dialog open={openAddDialog} onClose={() => setOpenAddDialog(false)}>
        <DialogTitle>Add Permission</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="User ID"
            value={newPermission.user_id}
            onChange={(e) => setNewPermission({ ...newPermission, user_id: e.target.value })}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Resource Type</InputLabel>
            <Select
              value={newPermission.resource_type}
              onChange={(e) => setNewPermission({ ...newPermission, resource_type: e.target.value })}
            >
              {resourceTypes.map(type => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Resource ID"
            value={newPermission.resource_id}
            onChange={(e) => setNewPermission({ ...newPermission, resource_id: e.target.value })}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Permission</InputLabel>
            <Select
              value={newPermission.permission}
              onChange={(e) => setNewPermission({ ...newPermission, permission: e.target.value })}
            >
              {availablePermissions.map(perm => (
                <MenuItem key={perm} value={perm}>{perm}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenAddDialog(false)}>Cancel</Button>
          <Button onClick={handleAddPermission} variant="contained" color="primary">
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Set Owner Dialog */}
      <Dialog open={openOwnerDialog} onClose={() => setOpenOwnerDialog(false)}>
        <DialogTitle>Set Resource Owner</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="User ID"
            value={newOwner.user_id}
            onChange={(e) => setNewOwner({ ...newOwner, user_id: e.target.value })}
            margin="normal"
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Resource Type</InputLabel>
            <Select
              value={newOwner.resource_type}
              onChange={(e) => setNewOwner({ ...newOwner, resource_type: e.target.value })}
            >
              {resourceTypes.map(type => (
                <MenuItem key={type} value={type}>{type}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Resource ID"
            value={newOwner.resource_id}
            onChange={(e) => setNewOwner({ ...newOwner, resource_id: e.target.value })}
            margin="normal"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenOwnerDialog(false)}>Cancel</Button>
          <Button onClick={handleSetOwner} variant="contained" color="primary">
            Set Owner
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminPermissions; 