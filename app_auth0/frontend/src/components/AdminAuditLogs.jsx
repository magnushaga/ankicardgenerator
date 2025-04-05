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
  TablePagination,
  TextField,
  IconButton,
  Chip,
  Alert,
  CircularProgress,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Tooltip,
  InputAdornment,
  Button
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Refresh as RefreshIcon,
  History as HistoryIcon,
  Person as PersonIcon,
  Security as SecurityIcon,
  School as SchoolIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { format } from 'date-fns';

// Helper function to get the appropriate icon for a resource type
const getResourceIcon = (resourceType) => {
  switch (resourceType?.toLowerCase()) {
    case 'user':
      return <PersonIcon fontSize="small" />;
    case 'role':
    case 'permission':
      return <SecurityIcon fontSize="small" />;
    case 'course':
    case 'textbook':
      return <SchoolIcon fontSize="small" />;
    case 'system':
    case 'settings':
      return <SettingsIcon fontSize="small" />;
    default:
      return <HistoryIcon fontSize="small" />;
  }
};

const AdminAuditLogs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [resourceTypeFilter, setResourceTypeFilter] = useState('all');
  const [actionFilter, setActionFilter] = useState('all');
  const [dateFilter, setDateFilter] = useState('all');
  const [resourceTypes, setResourceTypes] = useState([]);
  const [actionTypes, setActionTypes] = useState([]);

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [logs, searchQuery, resourceTypeFilter, actionFilter, dateFilter]);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const response = await fetch('http://localhost:5001/api/admin/audit-logs', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch audit logs');
      }

      const data = await response.json();
      setLogs(data.logs || []);
      
      // Extract unique resource types and actions for filters
      const resourceTypesSet = new Set(
        data.logs?.map(log => log.resource_type || 'System') || []
      );
      setResourceTypes(Array.from(resourceTypesSet));
      
      const actionTypesSet = new Set(
        data.logs?.map(log => log.action) || []
      );
      setActionTypes(Array.from(actionTypesSet));
      
      setLoading(false);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
      setError(err.message);
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...logs];

    // Apply search filter
    if (searchQuery) {
      const lowercaseQuery = searchQuery.toLowerCase();
      filtered = filtered.filter(log => 
        log.action?.toLowerCase().includes(lowercaseQuery) ||
        log.resource_type?.toLowerCase().includes(lowercaseQuery) ||
        log.admin_id?.toString().includes(lowercaseQuery) ||
        log.details?.toString().toLowerCase().includes(lowercaseQuery)
      );
    }

    // Apply resource type filter
    if (resourceTypeFilter !== 'all') {
      filtered = filtered.filter(log => 
        (log.resource_type || 'System') === resourceTypeFilter
      );
    }

    // Apply action filter
    if (actionFilter !== 'all') {
      filtered = filtered.filter(log => log.action === actionFilter);
    }

    // Apply date filter
    const now = new Date();
    if (dateFilter === 'today') {
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      filtered = filtered.filter(log => new Date(log.created_at) >= today);
    } else if (dateFilter === 'yesterday') {
      const yesterday = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
      filtered = filtered.filter(log => 
        new Date(log.created_at) >= yesterday && new Date(log.created_at) < today
      );
    } else if (dateFilter === 'week') {
      const lastWeek = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
      filtered = filtered.filter(log => new Date(log.created_at) >= lastWeek);
    } else if (dateFilter === 'month') {
      const lastMonth = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
      filtered = filtered.filter(log => new Date(log.created_at) >= lastMonth);
    }

    setFilteredLogs(filtered);
    setPage(0); // Reset to first page when filters change
  };

  const resetFilters = () => {
    setSearchQuery('');
    setResourceTypeFilter('all');
    setActionFilter('all');
    setDateFilter('all');
  };

  const handleRefresh = () => {
    fetchAuditLogs();
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
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
          Audit Logs
        </Typography>
        <Tooltip title="Refresh logs">
          <IconButton onClick={handleRefresh} color="primary">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            placeholder="Search logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              )
            }}
          />
        </Grid>
        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel id="resource-type-filter-label">Resource Type</InputLabel>
            <Select
              labelId="resource-type-filter-label"
              value={resourceTypeFilter}
              onChange={(e) => setResourceTypeFilter(e.target.value)}
              label="Resource Type"
            >
              <MenuItem value="all">All Types</MenuItem>
              {resourceTypes.map(type => (
                <MenuItem key={type} value={type}>
                  {type}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel id="action-filter-label">Action</InputLabel>
            <Select
              labelId="action-filter-label"
              value={actionFilter}
              onChange={(e) => setActionFilter(e.target.value)}
              label="Action"
            >
              <MenuItem value="all">All Actions</MenuItem>
              {actionTypes.map(action => (
                <MenuItem key={action} value={action}>
                  {action}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={2}>
          <FormControl fullWidth size="small">
            <InputLabel id="date-filter-label">Date Range</InputLabel>
            <Select
              labelId="date-filter-label"
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value)}
              label="Date Range"
            >
              <MenuItem value="all">All Time</MenuItem>
              <MenuItem value="today">Today</MenuItem>
              <MenuItem value="yesterday">Yesterday</MenuItem>
              <MenuItem value="week">Last 7 Days</MenuItem>
              <MenuItem value="month">Last 30 Days</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={2}>
          <Button 
            fullWidth 
            variant="outlined" 
            startIcon={<FilterIcon />}
            onClick={resetFilters}
            sx={{ height: '100%' }}
          >
            Reset Filters
          </Button>
        </Grid>
      </Grid>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Action</TableCell>
              <TableCell>Resource</TableCell>
              <TableCell>Admin</TableCell>
              <TableCell>IP Address</TableCell>
              <TableCell>Details</TableCell>
              <TableCell>Timestamp</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredLogs.length > 0 ? (
              filteredLogs
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((log) => (
                  <TableRow key={log.id}>
                    <TableCell>
                      <Chip 
                        label={log.action} 
                        size="small"
                        color={getActionColor(log.action)}
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getResourceIcon(log.resource_type)}
                        <Typography variant="body2">
                          {log.resource_type || 'System'}
                          {log.resource_id && (
                            <Typography 
                              component="span" 
                              variant="caption" 
                              color="text.secondary"
                              sx={{ ml: 0.5 }}
                            >
                              ({log.resource_id.substring(0, 8)}...)
                            </Typography>
                          )}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Tooltip title={log.admin_id || 'Unknown'}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <PersonIcon fontSize="small" />
                          <Typography variant="body2">
                            {log.admin_name || log.admin_id?.substring(0, 8) || 'Unknown'}
                          </Typography>
                        </Box>
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {log.ip_address || 'N/A'}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {log.details ? (
                        <Tooltip title={JSON.stringify(log.details, null, 2)}>
                          <Typography
                            variant="body2"
                            sx={{
                              maxWidth: 250,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap'
                            }}
                          >
                            {JSON.stringify(log.details)}
                          </Typography>
                        </Tooltip>
                      ) : (
                        <Typography variant="body2" color="text.secondary">
                          No details
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {formatDate(log.created_at)}
                      </Typography>
                    </TableCell>
                  </TableRow>
                ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} align="center">
                  <Typography variant="body2" color="text.secondary" sx={{ py: 2 }}>
                    No audit logs found
                  </Typography>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={filteredLogs.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>
    </Box>
  );
};

// Helper function to determine chip color based on action
const getActionColor = (action) => {
  const lowercaseAction = action?.toLowerCase() || '';
  
  if (lowercaseAction.includes('create') || lowercaseAction.includes('add')) {
    return 'success';
  } else if (lowercaseAction.includes('delete') || lowercaseAction.includes('remove')) {
    return 'error';
  } else if (lowercaseAction.includes('update') || lowercaseAction.includes('edit') || lowercaseAction.includes('modify')) {
    return 'primary';
  } else if (lowercaseAction.includes('login') || lowercaseAction.includes('logout')) {
    return 'secondary';
  } else {
    return 'default';
  }
};

// Helper function to format dates
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    return format(date, 'MMM d, yyyy h:mm a');
  } catch (error) {
    return dateString;
  }
};

export default AdminAuditLogs; 