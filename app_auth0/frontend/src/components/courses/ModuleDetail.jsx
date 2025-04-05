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
  List, 
  ListItem, 
  ListItemText, 
  ListItemIcon, 
  IconButton, 
  CircularProgress, 
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Description as DescriptionIcon,
  Assignment as AssignmentIcon,
  Quiz as QuizIcon,
  VideoLibrary as VideoIcon,
  Link as LinkIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  DragIndicator as DragIndicatorIcon
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';

const ModuleDetail = () => {
  const { courseId, moduleId } = useParams();
  const navigate = useNavigate();
  const [module, setModule] = useState(null);
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [openSectionDialog, setOpenSectionDialog] = useState(false);
  const [newSection, setNewSection] = useState({
    title: '',
    description: '',
    contentType: 'text',
    content: '',
    orderIndex: 0
  });

  useEffect(() => {
    const fetchModuleData = async () => {
      try {
        setLoading(true);
        
        // Fetch module details
        const moduleResponse = await fetch(`http://localhost:5001/api/courses/${courseId}/modules/${moduleId}`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!moduleResponse.ok) {
          throw new Error('Failed to fetch module details');
        }
        
        const moduleData = await moduleResponse.json();
        setModule(moduleData);
        
        // Fetch module sections
        const sectionsResponse = await fetch(`http://localhost:5001/api/courses/${courseId}/modules/${moduleId}/sections`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!sectionsResponse.ok) {
          throw new Error('Failed to fetch module sections');
        }
        
        const sectionsData = await sectionsResponse.json();
        setSections(sectionsData);
        
      } catch (err) {
        console.error('Error fetching module data:', err);
        setError('Failed to load module data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchModuleData();
  }, [courseId, moduleId]);

  const handleSectionDialogOpen = () => {
    setOpenSectionDialog(true);
  };

  const handleSectionDialogClose = () => {
    setOpenSectionDialog(false);
    setNewSection({
      title: '',
      description: '',
      contentType: 'text',
      content: '',
      orderIndex: sections.length
    });
  };

  const handleNewSectionChange = (e) => {
    const { name, value } = e.target;
    setNewSection({
      ...newSection,
      [name]: value
    });
  };

  const handleCreateSection = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/courses/${courseId}/modules/${moduleId}/sections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(newSection)
      });
      
      if (!response.ok) {
        throw new Error('Failed to create section');
      }
      
      const data = await response.json();
      setSections([...sections, data]);
      handleSectionDialogClose();
      
    } catch (err) {
      console.error('Error creating section:', err);
      setError('Failed to create section. Please try again.');
    }
  };

  const getContentIcon = (contentType) => {
    switch (contentType) {
      case 'text':
        return <DescriptionIcon />;
      case 'assignment':
        return <AssignmentIcon />;
      case 'quiz':
        return <QuizIcon />;
      case 'video':
        return <VideoIcon />;
      case 'link':
        return <LinkIcon />;
      default:
        return <DescriptionIcon />;
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

  if (!module) {
    return (
      <Box p={3}>
        <Alert severity="warning">Module not found</Alert>
        <Button 
          variant="contained" 
          color="primary" 
          onClick={() => navigate(`/courses/${courseId}`)}
          sx={{ mt: 2 }}
        >
          Back to Course
        </Button>
      </Box>
    );
  }

  return (
    <Box>
      {/* Module Header */}
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
            onClick={() => navigate(`/courses/${courseId}`)}
            sx={{ color: 'white', mr: 2 }}
          >
            Back
          </Button>
          <Typography variant="h4" component="h1">
            {module.title}
          </Typography>
        </Box>
        <Typography variant="subtitle1">
          {module.description}
        </Typography>
      </Paper>

      {/* Module Content */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h5">Module Content</Typography>
          <Button 
            variant="contained" 
            color="primary" 
            startIcon={<AddIcon />}
            onClick={handleSectionDialogOpen}
          >
            Add Content
          </Button>
        </Box>

        {sections.length === 0 ? (
          <Paper variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
            <DescriptionIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              No content yet
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Add content to your module to help students learn
            </Typography>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />}
              onClick={handleSectionDialogOpen}
            >
              Add Content
            </Button>
          </Paper>
        ) : (
          <List>
            {sections.map((section, index) => (
              <Accordion key={section.id}>
                <AccordionSummary
                  expandIcon={<ExpandMoreIcon />}
                  aria-controls={`section-${section.id}-content`}
                  id={`section-${section.id}-header`}
                >
                  <Box display="flex" alignItems="center" width="100%">
                    <DragIndicatorIcon sx={{ mr: 2, color: 'text.secondary' }} />
                    <ListItemIcon>
                      {getContentIcon(section.contentType)}
                    </ListItemIcon>
                    <ListItemText
                      primary={section.title}
                      secondary={section.description}
                    />
                    <Box>
                      <IconButton size="small" aria-label="edit">
                        <EditIcon />
                      </IconButton>
                      <IconButton size="small" aria-label="delete">
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Box p={2}>
                    {section.contentType === 'text' && (
                      <Typography>{section.content}</Typography>
                    )}
                    {section.contentType === 'assignment' && (
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            Assignment Details
                          </Typography>
                          <Typography variant="body2" paragraph>
                            {section.content}
                          </Typography>
                          <Button variant="contained" color="primary">
                            View Assignment
                          </Button>
                        </CardContent>
                      </Card>
                    )}
                    {section.contentType === 'quiz' && (
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            Quiz Details
                          </Typography>
                          <Typography variant="body2" paragraph>
                            {section.content}
                          </Typography>
                          <Button variant="contained" color="primary">
                            Take Quiz
                          </Button>
                        </CardContent>
                      </Card>
                    )}
                    {section.contentType === 'video' && (
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            Video Content
                          </Typography>
                          <Box 
                            sx={{ 
                              position: 'relative', 
                              paddingTop: '56.25%', 
                              mb: 2 
                            }}
                          >
                            <iframe
                              style={{
                                position: 'absolute',
                                top: 0,
                                left: 0,
                                width: '100%',
                                height: '100%'
                              }}
                              src={section.content}
                              frameBorder="0"
                              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                              allowFullScreen
                            />
                          </Box>
                        </CardContent>
                      </Card>
                    )}
                    {section.contentType === 'link' && (
                      <Card variant="outlined">
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            External Resource
                          </Typography>
                          <Typography variant="body2" paragraph>
                            {section.content}
                          </Typography>
                          <Button 
                            variant="contained" 
                            color="primary"
                            href={section.content}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            Visit Resource
                          </Button>
                        </CardContent>
                      </Card>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            ))}
          </List>
        )}
      </Paper>

      {/* Add Section Dialog */}
      <Dialog 
        open={openSectionDialog} 
        onClose={handleSectionDialogClose}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add New Content</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Content Title"
            type="text"
            fullWidth
            variant="outlined"
            value={newSection.title}
            onChange={handleNewSectionChange}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            name="description"
            label="Content Description"
            type="text"
            fullWidth
            multiline
            rows={2}
            variant="outlined"
            value={newSection.description}
            onChange={handleNewSectionChange}
            sx={{ mb: 2 }}
          />
          <TextField
            select
            margin="dense"
            name="contentType"
            label="Content Type"
            fullWidth
            variant="outlined"
            value={newSection.contentType}
            onChange={handleNewSectionChange}
            sx={{ mb: 2 }}
          >
            <MenuItem value="text">Text Content</MenuItem>
            <MenuItem value="assignment">Assignment</MenuItem>
            <MenuItem value="quiz">Quiz</MenuItem>
            <MenuItem value="video">Video</MenuItem>
            <MenuItem value="link">External Link</MenuItem>
          </TextField>
          <TextField
            margin="dense"
            name="content"
            label="Content"
            type="text"
            fullWidth
            multiline
            rows={4}
            variant="outlined"
            value={newSection.content}
            onChange={handleNewSectionChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleSectionDialogClose}>Cancel</Button>
          <Button onClick={handleCreateSection} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModuleDetail; 