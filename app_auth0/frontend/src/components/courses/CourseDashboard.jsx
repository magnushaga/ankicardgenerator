import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Grid, 
  Card, 
  CardContent, 
  CardActions, 
  Button, 
  Chip, 
  Divider,
  CircularProgress,
  IconButton,
  Tooltip
} from '@mui/material';
import { 
  Add as AddIcon, 
  School as SchoolIcon, 
  Book as BookIcon,
  Assignment as AssignmentIcon,
  Forum as ForumIcon,
  CalendarMonth as CalendarIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const CourseDashboard = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch courses from API
    const fetchCourses = async () => {
      try {
        setLoading(true);
        // Replace with actual API call
        const response = await fetch('http://localhost:5001/api/courses', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch courses');
        }
        
        const data = await response.json();
        setCourses(data);
      } catch (err) {
        console.error('Error fetching courses:', err);
        setError('Failed to load courses. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  const handleCreateCourse = () => {
    navigate('/courses/create');
  };

  const handleViewCourse = (courseId) => {
    navigate(`/courses/${courseId}`);
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
        <Typography color="error">{error}</Typography>
        <Button variant="contained" color="primary" onClick={() => window.location.reload()}>
          Retry
        </Button>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1">
          My Courses
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<AddIcon />}
          onClick={handleCreateCourse}
        >
          Create Course
        </Button>
      </Box>

      {courses.length === 0 ? (
        <Card>
          <CardContent>
            <Box display="flex" flexDirection="column" alignItems="center" py={4}>
              <SchoolIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary" gutterBottom>
                You don't have any courses yet
              </Typography>
              <Typography variant="body2" color="text.secondary" align="center" mb={2}>
                Create your first course to start organizing your study materials
              </Typography>
              <Button 
                variant="contained" 
                color="primary" 
                startIcon={<AddIcon />}
                onClick={handleCreateCourse}
              >
                Create Course
              </Button>
            </Box>
          </CardContent>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {courses.map((course) => (
            <Grid item xs={12} sm={6} md={4} key={course.id}>
              <Card 
                sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column',
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 3
                  }
                }}
              >
                <CardContent sx={{ flexGrow: 1 }}>
                  <Typography variant="h6" component="h2" gutterBottom>
                    {course.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {course.description || 'No description available'}
                  </Typography>
                  <Box display="flex" flexWrap="wrap" gap={1} mb={2}>
                    <Chip 
                      icon={<BookIcon />} 
                      label={`${course.moduleCount || 0} Modules`} 
                      size="small" 
                      variant="outlined" 
                    />
                    <Chip 
                      icon={<AssignmentIcon />} 
                      label={`${course.assignmentCount || 0} Assignments`} 
                      size="small" 
                      variant="outlined" 
                    />
                  </Box>
                  <Divider sx={{ my: 1 }} />
                  <Box display="flex" justifyContent="space-between" alignItems="center">
                    <Typography variant="caption" color="text.secondary">
                      Last updated: {new Date(course.updatedAt).toLocaleDateString()}
                    </Typography>
                    <Chip 
                      label={course.status || 'Active'} 
                      color={course.status === 'Active' ? 'success' : 'default'} 
                      size="small" 
                    />
                  </Box>
                </CardContent>
                <CardActions>
                  <Button 
                    size="small" 
                    color="primary" 
                    onClick={() => handleViewCourse(course.id)}
                  >
                    View Course
                  </Button>
                  <Box sx={{ flexGrow: 1 }} />
                  <Tooltip title="Course Calendar">
                    <IconButton size="small">
                      <CalendarIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Discussion Forum">
                    <IconButton size="small">
                      <ForumIcon />
                    </IconButton>
                  </Tooltip>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default CourseDashboard; 