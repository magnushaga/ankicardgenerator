import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardActions, 
  Divider, 
  TextField, 
  CircularProgress, 
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormHelperText,
  Tabs,
  Tab,
  Chip,
  IconButton,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Settings as SettingsIcon,
  Upload as UploadIcon,
  Description as DescriptionIcon,
  Link as LinkIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  AccessTime as AccessTimeIcon,
  Assignment as AssignmentIcon,
  Comment as CommentIcon,
  AttachFile as AttachFileIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`assignment-tabpanel-${index}`}
      aria-labelledby={`assignment-tab-${index}`}
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

const AssignmentDetail = () => {
  const { courseId, moduleId, assignmentId } = useParams();
  const navigate = useNavigate();
  const [assignment, setAssignment] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [openSettingsDialog, setOpenSettingsDialog] = useState(false);
  const [settings, setSettings] = useState({
    submissionType: 'text',
    fileTypes: ['pdf', 'doc', 'docx'],
    maxFileSize: 10,
    allowLateSubmissions: false,
    requireComments: false
  });

  useEffect(() => {
    const fetchAssignmentData = async () => {
      try {
        setLoading(true);
        
        // Fetch assignment details
        const assignmentResponse = await fetch(`http://localhost:5001/api/courses/${courseId}/modules/${moduleId}/assignments/${assignmentId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!assignmentResponse.ok) {
          throw new Error('Failed to fetch assignment details');
        }
        
        const assignmentData = await assignmentResponse.json();
        setAssignment(assignmentData);
        
        // Fetch user's submission if it exists
        const submissionResponse = await fetch(`http://localhost:5001/api/courses/${courseId}/modules/${moduleId}/assignments/${assignmentId}/submission`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (submissionResponse.ok) {
          const submissionData = await submissionResponse.json();
          setSubmission(submissionData);
        }
        
      } catch (err) {
        console.error('Error fetching assignment data:', err);
        setError('Failed to load assignment data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchAssignmentData();
  }, [courseId, moduleId, assignmentId]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleSettingsDialogOpen = () => {
    setOpenSettingsDialog(true);
  };

  const handleSettingsDialogClose = () => {
    setOpenSettingsDialog(false);
  };

  const handleSettingsChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings({
      ...settings,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const handleSaveSettings = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/courses/${courseId}/modules/${moduleId}/assignments/${assignmentId}/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(settings)
      });
      
      if (!response.ok) {
        throw new Error('Failed to update assignment settings');
      }
      
      handleSettingsDialogClose();
      
    } catch (err) {
      console.error('Error updating assignment settings:', err);
      setError('Failed to update assignment settings. Please try again.');
    }
  };

  const handleSubmitAssignment = async () => {
    try {
      // Implementation for submitting assignment
      // This would depend on the submission type (text, file, etc.)
      
      // For now, just show a success message
      setSubmission({
        id: 'temp-id',
        content: 'This is a sample submission',
        submittedAt: new Date().toISOString(),
        status: 'submitted'
      });
      
    } catch (err) {
      console.error('Error submitting assignment:', err);
      setError('Failed to submit assignment. Please try again.');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={3}>
        <Alert severity="error">{error}</Alert>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => window.location.reload()}
          sx={{ mt: 2 }}
        >
          Retry
        </Button>
      </Box>
    );
  }

  if (!assignment) {
    return (
      <Box p={3}>
        <Alert severity="warning">Assignment not found</Alert>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => navigate(`/courses/${courseId}/modules/${moduleId}`)}
          sx={{ mt: 2 }}
        >
          Back to Module
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Assignment Header */}
      <Paper 
        elevation={0} 
        sx={{ 
          p: 3, 
          mb: 3, 
          background: 'linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)',
          color: 'white'
        }}
      >
        <Box display="flex" alignItems="center" mb={2}>
          <Button 
            startIcon={<ArrowBackIcon />} 
            onClick={() => navigate(`/courses/${courseId}/modules/${moduleId}`)}
            sx={{ color: 'white', mr: 2 }}
          >
            Back
          </Button>
          <Typography variant="h4" component="h1">
            {assignment.title}
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" flexWrap="wrap" gap={1}>
          <Chip 
            icon={<AssignmentIcon />} 
            label={assignment.assignmentType || 'Assignment'} 
            sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)' }} 
          />
          {assignment.dueDate && (
            <Chip 
              icon={<AccessTimeIcon />} 
              label={`Due: ${new Date(assignment.dueDate).toLocaleDateString()}`} 
              sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)' }} 
            />
          )}
          {assignment.pointsPossible && (
            <Chip 
              label={`${assignment.pointsPossible} points`} 
              sx={{ bgcolor: 'rgba(255, 255, 255, 0.2)' }} 
            />
          )}
        </Box>
      </Paper>

      {/* Assignment Content */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
              <Typography variant="h5">Assignment Details</Typography>
              <Tooltip title="Assignment Settings">
                <IconButton onClick={handleSettingsDialogOpen}>
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
            </Box>
            
            <Typography variant="body1" paragraph>
              {assignment.description}
            </Typography>
            
            <Divider sx={{ my: 3 }} />
            
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={tabValue} onChange={handleTabChange} aria-label="assignment tabs">
                <Tab label="Instructions" id="assignment-tab-0" aria-controls="assignment-tabpanel-0" />
                <Tab label="Submission" id="assignment-tab-1" aria-controls="assignment-tabpanel-1" />
                {submission && <Tab label="Feedback" id="assignment-tab-2" aria-controls="assignment-tabpanel-2" />}
              </Tabs>
            </Box>
            
            <TabPanel value={tabValue} index={0}>
              <Typography variant="body1" paragraph>
                {assignment.instructions || 'No specific instructions provided for this assignment.'}
              </Typography>
              
              {assignment.attachments && assignment.attachments.length > 0 && (
                <Box mt={3}>
                  <Typography variant="h6" gutterBottom>
                    Attachments
                  </Typography>
                  <List>
                    {assignment.attachments.map((attachment, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <AttachFileIcon />
                        </ListItemIcon>
                        <ListItemText 
                          primary={attachment.name} 
                          secondary={`${attachment.size} KB`} 
                        />
                        <ListItemSecondaryAction>
                          <Button 
                            variant="outlined" 
                            size="small"
                            href={attachment.url}
                            target="_blank"
                          >
                            Download
                          </Button>
                        </ListItemSecondaryAction>
                      </ListItem>
                    ))}
                  </List>
                </Box>
              )}
            </TabPanel>
            
            <TabPanel value={tabValue} index={1}>
              {submission ? (
                <Box>
                  <Alert 
                    severity={submission.status === 'graded' ? 'success' : 'info'} 
                    sx={{ mb: 3 }}
                  >
                    {submission.status === 'graded' 
                      ? 'Your assignment has been graded.' 
                      : 'Your assignment has been submitted and is awaiting grading.'}
                  </Alert>
                  
                  <Typography variant="h6" gutterBottom>
                    Your Submission
                  </Typography>
                  
                  <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                    <Typography variant="body1">
                      {submission.content}
                    </Typography>
                  </Paper>
                  
                  <Typography variant="body2" color="text.secondary">
                    Submitted on: {new Date(submission.submittedAt).toLocaleString()}
                  </Typography>
                  
                  <Box mt={3}>
                    <Button 
                      variant="outlined" 
                      color="primary"
                      onClick={() => setSubmission(null)}
                    >
                      Edit Submission
                    </Button>
                  </Box>
                </Box>
              ) : (
                <Box>
                  <Typography variant="body1" paragraph>
                    Submit your assignment below. You can submit text directly or upload files depending on the assignment requirements.
                  </Typography>
                  
                  <TextField
                    fullWidth
                    multiline
                    rows={6}
                    label="Your Submission"
                    variant="outlined"
                    sx={{ mb: 3 }}
                  />
                  
                  <Box display="flex" alignItems="center" mb={3}>
                    <Button 
                      variant="outlined" 
                      startIcon={<UploadIcon />}
                      sx={{ mr: 2 }}
                    >
                      Upload Files
                    </Button>
                    <Typography variant="body2" color="text.secondary">
                      Supported formats: PDF, DOC, DOCX (Max size: 10MB)
                    </Typography>
                  </Box>
                  
                  <Button 
                    variant="contained" 
                    color="primary"
                    startIcon={<SaveIcon />}
                    onClick={handleSubmitAssignment}
                  >
                    Submit Assignment
                  </Button>
                </Box>
              )}
            </TabPanel>
            
            {submission && (
              <TabPanel value={tabValue} index={2}>
                {submission.status === 'graded' ? (
                  <Box>
                    <Box display="flex" alignItems="center" mb={3}>
                      <Typography variant="h6" sx={{ mr: 2 }}>
                        Grade: {submission.grade} / {assignment.pointsPossible}
                      </Typography>
                      <Chip 
                        icon={<CheckCircleIcon />} 
                        label="Graded" 
                        color="success" 
                      />
                    </Box>
                    
                    <Typography variant="h6" gutterBottom>
                      Feedback
                    </Typography>
                    
                    <Paper variant="outlined" sx={{ p: 2, mb: 3 }}>
                      <Typography variant="body1">
                        {submission.feedback || 'No feedback provided.'}
                      </Typography>
                    </Paper>
                    
                    <Typography variant="body2" color="text.secondary">
                      Graded on: {new Date(submission.gradedAt).toLocaleString()}
                    </Typography>
                  </Box>
                ) : (
                  <Alert severity="info">
                    Your submission is still being reviewed. Check back later for feedback.
                  </Alert>
                )}
              </TabPanel>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Assignment Information
            </Typography>
            
            <List>
              <ListItem>
                <ListItemIcon>
                  <AssignmentIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="Type" 
                  secondary={assignment.assignmentType || 'Standard Assignment'} 
                />
              </ListItem>
              
              {assignment.dueDate && (
                <ListItem>
                  <ListItemIcon>
                    <AccessTimeIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Due Date" 
                    secondary={new Date(assignment.dueDate).toLocaleString()} 
                  />
                </ListItem>
              )}
              
              {assignment.pointsPossible && (
                <ListItem>
                  <ListItemIcon>
                    <CheckCircleIcon />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Points" 
                    secondary={assignment.pointsPossible} 
                  />
                </ListItem>
              )}
              
              <ListItem>
                <ListItemIcon>
                  <CommentIcon />
                </ListItemIcon>
                <ListItemText 
                  primary="Comments" 
                  secondary="0 comments" 
                />
              </ListItem>
            </List>
            
            <Divider sx={{ my: 2 }} />
            
            <Typography variant="h6" gutterBottom>
              Submission Status
            </Typography>
            
            {submission ? (
              <Alert 
                severity={submission.status === 'graded' ? 'success' : 'info'} 
                sx={{ mb: 2 }}
              >
                {submission.status === 'graded' 
                  ? 'Your assignment has been graded.' 
                  : 'Your assignment has been submitted and is awaiting grading.'}
              </Alert>
            ) : (
              <Alert severity="warning" sx={{ mb: 2 }}>
                You haven't submitted this assignment yet.
              </Alert>
            )}
            
            <Button 
              variant="contained" 
              color="primary" 
              fullWidth
              onClick={() => setTabValue(1)}
            >
              {submission ? 'View Submission' : 'Submit Assignment'}
            </Button>
          </Paper>
          
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Discussion
            </Typography>
            
            <Typography variant="body2" color="text.secondary" paragraph>
              Have questions about this assignment? Start a discussion with your instructor and classmates.
            </Typography>
            
            <Button 
              variant="outlined" 
              fullWidth
              startIcon={<CommentIcon />}
            >
              Start Discussion
            </Button>
          </Paper>
        </Grid>
      </Grid>

      {/* Settings Dialog */}
      <Dialog 
        open={openSettingsDialog} 
        onClose={handleSettingsDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Assignment Settings</DialogTitle>
        <DialogContent>
          <FormControl fullWidth sx={{ mt: 2, mb: 2 }}>
            <InputLabel>Submission Type</InputLabel>
            <Select
              name="submissionType"
              value={settings.submissionType}
              onChange={handleSettingsChange}
              label="Submission Type"
            >
              <MenuItem value="text">Text Entry</MenuItem>
              <MenuItem value="file">File Upload</MenuItem>
              <MenuItem value="both">Text Entry and File Upload</MenuItem>
              <MenuItem value="external">External Tool</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Allowed File Types</InputLabel>
            <Select
              name="fileTypes"
              multiple
              value={settings.fileTypes}
              onChange={handleSettingsChange}
              label="Allowed File Types"
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {selected.map((value) => (
                    <Chip key={value} label={value} />
                  ))}
                </Box>
              )}
            >
              <MenuItem value="pdf">PDF</MenuItem>
              <MenuItem value="doc">DOC</MenuItem>
              <MenuItem value="docx">DOCX</MenuItem>
              <MenuItem value="txt">TXT</MenuItem>
              <MenuItem value="jpg">JPG</MenuItem>
              <MenuItem value="png">PNG</MenuItem>
            </Select>
            <FormHelperText>Select the file types that students can upload</FormHelperText>
          </FormControl>
          
          <TextField
            fullWidth
            type="number"
            name="maxFileSize"
            label="Maximum File Size (MB)"
            value={settings.maxFileSize}
            onChange={handleSettingsChange}
            sx={{ mb: 2 }}
          />
          
          <FormControl fullWidth sx={{ mb: 2 }}>
            <InputLabel>Late Submission Policy</InputLabel>
            <Select
              name="allowLateSubmissions"
              value={settings.allowLateSubmissions}
              onChange={handleSettingsChange}
              label="Late Submission Policy"
            >
              <MenuItem value={false}>Not Allowed</MenuItem>
              <MenuItem value={true}>Allowed with Penalty</MenuItem>
            </Select>
          </FormControl>
          
          <FormControl fullWidth>
            <InputLabel>Comments</InputLabel>
            <Select
              name="requireComments"
              value={settings.requireComments}
              onChange={handleSettingsChange}
              label="Comments"
            >
              <MenuItem value={false}>Optional</MenuItem>
              <MenuItem value={true}>Required</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSettingsDialogClose}>Cancel</Button>
          <Button onClick={handleSaveSettings} variant="contained" color="primary">
            Save Settings
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AssignmentDetail; 