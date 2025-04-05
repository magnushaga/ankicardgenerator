import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Tabs, 
  Tab, 
  Button, 
  Grid, 
  Card, 
  CardContent, 
  CardActions, 
  Divider, 
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  IconButton, 
  Chip, 
  CircularProgress, 
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Tooltip
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Book as BookIcon,
  Assignment as AssignmentIcon,
  Forum as ForumIcon,
  People as PeopleIcon,
  Settings as SettingsIcon,
  Folder as FolderIcon,
  Description as DescriptionIcon,
  Quiz as QuizIcon,
  VideoLibrary as VideoIcon,
  Link as LinkIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';

// TabPanel component for tab content
function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`course-tabpanel-${index}`}
      aria-labelledby={`course-tab-${index}`}
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

const CourseDetail = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const [course, setCourse] = useState(null);
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tabValue, setTabValue] = useState(0);
  const [openModuleDialog, setOpenModuleDialog] = useState(false);
  const [newModule, setNewModule] = useState({
    title: '',
    description: '',
    orderIndex: 0
  });

  useEffect(() => {
    const fetchCourseData = async () => {
      try {
        setLoading(true);
        
        // Fetch course details
        const courseResponse = await fetch(`http://localhost:5001/api/courses/${courseId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!courseResponse.ok) {
          throw new Error('Failed to fetch course details');
        }
        
        const courseData = await courseResponse.json();
        setCourse(courseData);
        
        // Fetch course modules
        const modulesResponse = await fetch(`http://localhost:5001/api/courses/${courseId}/modules`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!modulesResponse.ok) {
          throw new Error('Failed to fetch course modules');
        }
        
        const modulesData = await modulesResponse.json();
        setModules(modulesData);
        
      } catch (err) {
        console.error('Error fetching course data:', err);
        setError('Failed to load course data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourseData();
  }, [courseId]);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleModuleDialogOpen = () => {
    setOpenModuleDialog(true);
  };

  const handleModuleDialogClose = () => {
    setOpenModuleDialog(false);
    setNewModule({
      title: '',
      description: '',
      orderIndex: modules.length
    });
  };

  const handleNewModuleChange = (e) => {
    const { name, value } = e.target;
    setNewModule({
      ...newModule,
      [name]: value
    });
  };

  const handleCreateModule = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/courses/${courseId}/modules`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(newModule)
      });
      
      if (!response.ok) {
        throw new Error('Failed to create module');
      }
      
      const data = await response.json();
      setModules([...modules, data]);
      handleModuleDialogClose();
      
    } catch (err) {
      console.error('Error creating module:', err);
      setError('Failed to create module. Please try again.');
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

  if (!course) {
    return (
      <Box p={3}>
        <Alert severity="warning">Course not found</Alert>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => navigate('/courses')}
          sx={{ mt: 2 }}
        >
          Back to Courses
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Course Header */}
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
            onClick={() => navigate('/courses')}
            sx={{ color: 'white', mr: 2 }}
          >
            Back
          </Button>
          <Typography variant="h4" component="h1">
            {course.title}
          </Typography>
        </Box>
        <Typography variant="subtitle1" sx={{ mb: 2 }}>
          {course.description}
        </Typography>
        <Box display="flex" flexWrap="wrap" gap={1}>
          <Chip label={course.subject} size="small" sx={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }} />
          <Chip label={course.level} size="small" sx={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }} />
          {course.institution && (
            <Chip label={course.institution} size="small" sx={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }} />
          )}
          {course.department && (
            <Chip label={course.department} size="small" sx={{ backgroundColor: 'rgba(255, 255, 255, 0.2)' }} />
          )}
        </Box>
      </Paper>

      {/* Course Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<BookIcon />} label="Modules" />
          <Tab icon={<AssignmentIcon />} label="Assignments" />
          <Tab icon={<QuizIcon />} label="Quizzes" />
          <Tab icon={<ForumIcon />} label="Discussions" />
          <Tab icon={<PeopleIcon />} label="People" />
          <Tab icon={<SettingsIcon />} label="Settings" />
        </Tabs>
      </Paper>

      {/* Modules Tab */}
      <TabPanel value={tabValue} index={0}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">Course Modules</Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
            onClick={handleModuleDialogOpen}
          >
            Add Module
          </Button>
        </Box>

        {modules.length === 0 ? (
          <Paper variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
            <FolderIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No modules yet
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Create your first module to start organizing your course content
            </Typography>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />}
              onClick={handleModuleDialogOpen}
            >
              Create Module
            </Button>
          </Paper>
        ) : (
          <List>
            {modules.map((module, index) => (
              <Paper 
                key={module.id} 
                variant="outlined" 
                sx={{ mb: 2 }}
              >
                <ListItem
                  secondaryAction={
                    <Box>
                      <IconButton edge="end" aria-label="edit">
                        <EditIcon />
                      </IconButton>
                      <IconButton edge="end" aria-label="delete">
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  }
                >
                  <ListItemIcon>
                    <FolderIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={module.title}
                    secondary={module.description}
                  />
                </ListItem>
                <Divider />
                <Box p={2}>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box display="flex" alignItems="center">
                            <DescriptionIcon sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="body2">
                              {module.sectionCount || 0} Sections
                            </Typography>
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button size="small">View Sections</Button>
                        </CardActions>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box display="flex" alignItems="center">
                            <AssignmentIcon sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="body2">
                              {module.assignmentCount || 0} Assignments
                            </Typography>
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button size="small">View Assignments</Button>
                        </CardActions>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box display="flex" alignItems="center">
                            <QuizIcon sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="body2">
                              {module.quizCount || 0} Quizzes
                            </Typography>
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button size="small">View Quizzes</Button>
                        </CardActions>
                      </Card>
                    </Grid>
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box display="flex" alignItems="center">
                            <VideoIcon sx={{ mr: 1, color: 'primary.main' }} />
                            <Typography variant="body2">
                              {module.videoCount || 0} Videos
                            </Typography>
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button size="small">View Videos</Button>
                        </CardActions>
                      </Card>
                    </Grid>
                  </Grid>
                </Box>
              </Paper>
            ))}
          </List>
        )}
      </TabPanel>

      {/* Assignments Tab */}
      <TabPanel value={tabValue} index={1}>
        <Typography variant="h5" gutterBottom>Assignments</Typography>
        <Paper variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
          <AssignmentIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No assignments yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Create assignments to assess student learning
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
          >
            Create Assignment
          </Button>
        </Paper>
      </TabPanel>

      {/* Quizzes Tab */}
      <TabPanel value={tabValue} index={2}>
        <Typography variant="h5" gutterBottom>Quizzes</Typography>
        <Paper variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
          <QuizIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No quizzes yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Create quizzes to test student knowledge
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
          >
            Create Quiz
          </Button>
        </Paper>
      </TabPanel>

      {/* Discussions Tab */}
      <TabPanel value={tabValue} index={3}>
        <Typography variant="h5" gutterBottom>Discussions</Typography>
        <Paper variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
          <ForumIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No discussions yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Create discussion topics to encourage student engagement
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
          >
            Create Discussion
          </Button>
        </Paper>
      </TabPanel>

      {/* People Tab */}
      <TabPanel value={tabValue} index={4}>
        <Typography variant="h5" gutterBottom>People</Typography>
        <Paper variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
          <PeopleIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No enrolled students yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Invite students to enroll in your course
          </Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
          >
            Invite Students
          </Button>
        </Paper>
      </TabPanel>

      {/* Settings Tab */}
      <TabPanel value={tabValue} index={5}>
        <Typography variant="h5" gutterBottom>Course Settings</Typography>
        <Paper variant="outlined" sx={{ p: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>General Settings</Typography>
              <Box mb={3}>
                <Typography variant="subtitle2" gutterBottom>Course Visibility</Typography>
                <Chip label="Private" color="default" sx={{ mr: 1 }} />
                <Chip label="Public" variant="outlined" />
              </Box>
              <Box mb={3}>
                <Typography variant="subtitle2" gutterBottom>Enrollment</Typography>
                <Chip label="Open" color="default" sx={{ mr: 1 }} />
                <Chip label="Invite Only" variant="outlined" sx={{ mr: 1 }} />
                <Chip label="Requires Approval" variant="outlined" />
              </Box>
              <Box mb={3}>
                <Typography variant="subtitle2" gutterBottom>Language</Typography>
                <Chip label="English" color="default" />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>Advanced Settings</Typography>
              <Box mb={3}>
                <Typography variant="subtitle2" gutterBottom>Course Format</Typography>
                <Chip label="Weekly" color="default" sx={{ mr: 1 }} />
                <Chip label="Topics" variant="outlined" />
              </Box>
              <Box mb={3}>
                <Typography variant="subtitle2" gutterBottom>Grading Scheme</Typography>
                <Chip label="Percentage" color="default" />
              </Box>
              <Box mb={3}>
                <Typography variant="subtitle2" gutterBottom>Time Zone</Typography>
                <Chip label="UTC" color="default" />
              </Box>
            </Grid>
          </Grid>
          <Divider sx={{ my: 3 }} />
          <Box display="flex" justifyContent="flex-end">
            <Button variant="contained" color="primary">
              Save Settings
            </Button>
          </Box>
        </Paper>
      </TabPanel>

      {/* Add Module Dialog */}
      <Dialog open={openModuleDialog} onClose={handleModuleDialogClose}>
        <DialogTitle>Create New Module</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Module Title"
            type="text"
            fullWidth
            variant="outlined"
            value={newModule.title}
            onChange={handleNewModuleChange}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="description"
            label="Module Description"
            type="text"
            fullWidth
            multiline
            rows={3}
            variant="outlined"
            value={newModule.description}
            onChange={handleNewModuleChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleModuleDialogClose}>Cancel</Button>
          <Button onClick={handleCreateModule} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CourseDetail; 