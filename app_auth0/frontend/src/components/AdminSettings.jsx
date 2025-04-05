import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Switch,
  FormControlLabel,
  Button,
  Card,
  CardContent,
  CardHeader,
  Divider,
  Alert,
  CircularProgress,
  Snackbar,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Email as EmailIcon,
  Storage as StorageIcon
} from '@mui/icons-material';

const AdminSettings = () => {
  const [settings, setSettings] = useState({
    general: {
      siteName: 'StudIQ',
      siteDescription: 'Learning Platform for Students',
      supportEmail: 'support@studiq.io',
      maxFileUploadSize: 10,
      defaultLanguage: 'en',
      allowUserRegistration: true
    },
    security: {
      passwordMinLength: 8,
      passwordRequireUppercase: true,
      passwordRequireNumbers: true,
      passwordRequireSpecialChars: true,
      sessionTimeout: 30,
      maxLoginAttempts: 5
    },
    notification: {
      emailNotifications: true,
      adminAlerts: true,
      userActivityEmails: true,
      marketingEmails: false
    },
    storage: {
      storageProvider: 'supabase',
      defaultBucket: 'app-storage',
      maxStoragePerUser: 100
    }
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  // Languages for select menu
  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' }
  ];

  // Storage providers for select menu
  const storageProviders = [
    { value: 'supabase', label: 'Supabase Storage' },
    { value: 's3', label: 'Amazon S3' },
    { value: 'gcs', label: 'Google Cloud Storage' },
    { value: 'azure', label: 'Azure Blob Storage' }
  ];

  useEffect(() => {
    // Simulate fetching settings from API
    const fetchSettings = async () => {
      try {
        setLoading(true);
        // In a real implementation, this would be an API call
        // const token = localStorage.getItem('access_token');
        // const response = await fetch('http://localhost:5001/api/admin/settings', {
        //   headers: {
        //     'Authorization': `Bearer ${token}`,
        //     'Content-Type': 'application/json'
        //   }
        // });
        
        // if (!response.ok) {
        //   throw new Error('Failed to fetch settings');
        // }
        
        // const data = await response.json();
        // setSettings(data);

        // For now, just use the default settings after a timeout to simulate API call
        setTimeout(() => {
          setLoading(false);
        }, 1000);
      } catch (err) {
        console.error('Error fetching settings:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleChange = (section, setting, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [setting]: value
      }
    }));
  };

  const handleRefresh = () => {
    setLoading(true);
    // In a real implementation, this would refetch the settings
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // In a real implementation, this would be an API call
      // const token = localStorage.getItem('access_token');
      // const response = await fetch('http://localhost:5001/api/admin/settings', {
      //   method: 'PUT',
      //   headers: {
      //     'Authorization': `Bearer ${token}`,
      //     'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify(settings)
      // });
      
      // if (!response.ok) {
      //   throw new Error('Failed to save settings');
      // }
      
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccess(true);
      setSaving(false);
    } catch (err) {
      console.error('Error saving settings:', err);
      setError(err.message);
      setSaving(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
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
          System Settings
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Tooltip title="Refresh settings">
            <IconButton onClick={handleRefresh} disabled={saving}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            color="primary"
            startIcon={<SaveIcon />}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="General Settings" 
              avatar={<SettingsIcon color="primary" />}
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Site Name"
                    value={settings.general.siteName}
                    onChange={(e) => handleChange('general', 'siteName', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Site Description"
                    value={settings.general.siteDescription}
                    onChange={(e) => handleChange('general', 'siteDescription', e.target.value)}
                    margin="normal"
                    multiline
                    rows={2}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Support Email"
                    value={settings.general.supportEmail}
                    onChange={(e) => handleChange('general', 'supportEmail', e.target.value)}
                    margin="normal"
                    type="email"
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Max File Upload Size (MB)"
                    value={settings.general.maxFileUploadSize}
                    onChange={(e) => handleChange('general', 'maxFileUploadSize', 
                      Number(e.target.value) || settings.general.maxFileUploadSize)}
                    margin="normal"
                    type="number"
                    inputProps={{ min: 1, max: 100 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="default-language-label">Default Language</InputLabel>
                    <Select
                      labelId="default-language-label"
                      value={settings.general.defaultLanguage}
                      onChange={(e) => handleChange('general', 'defaultLanguage', e.target.value)}
                      label="Default Language"
                    >
                      {languages.map(lang => (
                        <MenuItem key={lang.code} value={lang.code}>{lang.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.general.allowUserRegistration}
                        onChange={(e) => handleChange('general', 'allowUserRegistration', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Allow User Registration"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Security Settings" 
              avatar={<SecurityIcon color="primary" />}
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Minimum Password Length"
                    value={settings.security.passwordMinLength}
                    onChange={(e) => handleChange('security', 'passwordMinLength', 
                      Number(e.target.value) || settings.security.passwordMinLength)}
                    margin="normal"
                    type="number"
                    inputProps={{ min: 6, max: 32 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Session Timeout (minutes)"
                    value={settings.security.sessionTimeout}
                    onChange={(e) => handleChange('security', 'sessionTimeout', 
                      Number(e.target.value) || settings.security.sessionTimeout)}
                    margin="normal"
                    type="number"
                    inputProps={{ min: 5, max: 120 }}
                  />
                </Grid>
                <Grid item xs={12} sm={6}>
                  <TextField
                    fullWidth
                    label="Max Login Attempts"
                    value={settings.security.maxLoginAttempts}
                    onChange={(e) => handleChange('security', 'maxLoginAttempts', 
                      Number(e.target.value) || settings.security.maxLoginAttempts)}
                    margin="normal"
                    type="number"
                    inputProps={{ min: 3, max: 10 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="subtitle2" gutterBottom>
                    Password Requirements
                  </Typography>
                  <Grid container>
                    <Grid item xs={12}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings.security.passwordRequireUppercase}
                            onChange={(e) => handleChange('security', 'passwordRequireUppercase', e.target.checked)}
                            color="primary"
                          />
                        }
                        label="Require Uppercase Letters"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings.security.passwordRequireNumbers}
                            onChange={(e) => handleChange('security', 'passwordRequireNumbers', e.target.checked)}
                            color="primary"
                          />
                        }
                        label="Require Numbers"
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <FormControlLabel
                        control={
                          <Switch
                            checked={settings.security.passwordRequireSpecialChars}
                            onChange={(e) => handleChange('security', 'passwordRequireSpecialChars', e.target.checked)}
                            color="primary"
                          />
                        }
                        label="Require Special Characters"
                      />
                    </Grid>
                  </Grid>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Notification Settings" 
              avatar={<NotificationsIcon color="primary" />}
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Grid container>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notification.emailNotifications}
                        onChange={(e) => handleChange('notification', 'emailNotifications', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Enable Email Notifications"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notification.adminAlerts}
                        onChange={(e) => handleChange('notification', 'adminAlerts', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Admin Alert Notifications"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notification.userActivityEmails}
                        onChange={(e) => handleChange('notification', 'userActivityEmails', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="User Activity Emails"
                  />
                </Grid>
                <Grid item xs={12}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={settings.notification.marketingEmails}
                        onChange={(e) => handleChange('notification', 'marketingEmails', e.target.checked)}
                        color="primary"
                      />
                    }
                    label="Marketing Emails"
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader 
              title="Storage Settings" 
              avatar={<StorageIcon color="primary" />}
              titleTypographyProps={{ variant: 'h6' }}
            />
            <Divider />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <FormControl fullWidth margin="normal">
                    <InputLabel id="storage-provider-label">Storage Provider</InputLabel>
                    <Select
                      labelId="storage-provider-label"
                      value={settings.storage.storageProvider}
                      onChange={(e) => handleChange('storage', 'storageProvider', e.target.value)}
                      label="Storage Provider"
                    >
                      {storageProviders.map(provider => (
                        <MenuItem key={provider.value} value={provider.value}>{provider.label}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Default Bucket Name"
                    value={settings.storage.defaultBucket}
                    onChange={(e) => handleChange('storage', 'defaultBucket', e.target.value)}
                    margin="normal"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Max Storage Per User (MB)"
                    value={settings.storage.maxStoragePerUser}
                    onChange={(e) => handleChange('storage', 'maxStoragePerUser', 
                      Number(e.target.value) || settings.storage.maxStoragePerUser)}
                    margin="normal"
                    type="number"
                    inputProps={{ min: 10, max: 10000 }}
                  />
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<SaveIcon />}
          onClick={handleSave}
          disabled={saving}
          size="large"
        >
          {saving ? 'Saving...' : 'Save All Settings'}
        </Button>
      </Box>

      <Snackbar
        open={success}
        autoHideDuration={4000}
        onClose={handleCloseSnackbar}
        message="Settings saved successfully"
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Box>
  );
};

export default AdminSettings; 