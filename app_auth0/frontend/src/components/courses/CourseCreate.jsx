import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  TextField, 
  Button, 
  Paper, 
  Grid, 
  FormControl, 
  InputLabel, 
  Select, 
  MenuItem, 
  FormHelperText,
  Stepper,
  Step,
  StepLabel,
  Divider,
  Alert,
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  School as SchoolIcon
} from '@mui/icons-material';

const steps = ['Basic Information', 'Course Structure', 'Settings'];

const CourseCreate = () => {
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    subject: '',
    level: 'intermediate',
    isPublic: false,
    language: 'en',
    institution: '',
    department: '',
    courseCode: '',
    semester: '',
    year: new Date().getFullYear(),
    startDate: '',
    endDate: '',
    enrollmentType: 'open',
    maxEnrollments: 100
  });

  const [errors, setErrors] = useState({});

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    
    // Clear error when field is edited
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };

  const validateStep = () => {
    const newErrors = {};
    
    if (activeStep === 0) {
      if (!formData.title.trim()) {
        newErrors.title = 'Course title is required';
      }
      if (!formData.description.trim()) {
        newErrors.description = 'Course description is required';
      }
      if (!formData.subject.trim()) {
        newErrors.subject = 'Subject is required';
      }
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep()) {
      setActiveStep((prevStep) => prevStep + 1);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep()) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // Replace with actual API call
      const response = await fetch('http://localhost:5001/api/courses', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        throw new Error('Failed to create course');
      }
      
      const data = await response.json();
      setSuccess(true);
      
      // Redirect to the new course after a short delay
      setTimeout(() => {
        navigate(`/courses/${data.id}`);
      }, 1500);
      
    } catch (err) {
      console.error('Error creating course:', err);
      setError('Failed to create course. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Course Title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                error={!!errors.title}
                helperText={errors.title}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                multiline
                rows={4}
                label="Course Description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                error={!!errors.description}
                helperText={errors.description}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                label="Subject"
                name="subject"
                value={formData.subject}
                onChange={handleChange}
                error={!!errors.subject}
                helperText={errors.subject}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Difficulty Level</InputLabel>
                <Select
                  name="level"
                  value={formData.level}
                  onChange={handleChange}
                  label="Difficulty Level"
                >
                  <MenuItem value="beginner">Beginner</MenuItem>
                  <MenuItem value="intermediate">Intermediate</MenuItem>
                  <MenuItem value="advanced">Advanced</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Institution"
                name="institution"
                value={formData.institution}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Department"
                name="department"
                value={formData.department}
                onChange={handleChange}
              />
            </Grid>
          </Grid>
        );
      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Course Structure
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                You can add modules and sections after creating the course.
              </Typography>
              <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle1" gutterBottom>
                  Default Structure
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Your course will be created with a basic structure that you can customize later.
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        );
      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Course Code"
                name="courseCode"
                value={formData.courseCode}
                onChange={handleChange}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Semester</InputLabel>
                <Select
                  name="semester"
                  value={formData.semester}
                  onChange={handleChange}
                  label="Semester"
                >
                  <MenuItem value="fall">Fall</MenuItem>
                  <MenuItem value="spring">Spring</MenuItem>
                  <MenuItem value="summer">Summer</MenuItem>
                  <MenuItem value="winter">Winter</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Year"
                name="year"
                value={formData.year}
                onChange={handleChange}
                InputProps={{ inputProps: { min: 2000, max: 2100 } }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Enrollment Type</InputLabel>
                <Select
                  name="enrollmentType"
                  value={formData.enrollmentType}
                  onChange={handleChange}
                  label="Enrollment Type"
                >
                  <MenuItem value="open">Open</MenuItem>
                  <MenuItem value="invite">Invite Only</MenuItem>
                  <MenuItem value="approval">Requires Approval</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                type="number"
                label="Maximum Enrollments"
                name="maxEnrollments"
                value={formData.maxEnrollments}
                onChange={handleChange}
                InputProps={{ inputProps: { min: 1 } }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Language</InputLabel>
                <Select
                  name="language"
                  value={formData.language}
                  onChange={handleChange}
                  label="Language"
                >
                  <MenuItem value="en">English</MenuItem>
                  <MenuItem value="es">Spanish</MenuItem>
                  <MenuItem value="fr">French</MenuItem>
                  <MenuItem value="de">German</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        );
      default:
        return null;
    }
  };

  return (
    <Box p={3}>
      <Box display="flex" alignItems="center" mb={4}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/courses')}
          sx={{ mr: 2 }}
        >
          Back
        </Button>
        <Typography variant="h4" component="h1">
          Create New Course
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Course created successfully! Redirecting...
        </Alert>
      )}

      <Paper sx={{ p: 3, mb: 4 }}>
        <Stepper activeStep={activeStep} alternativeLabel>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
      </Paper>

      <Paper sx={{ p: 3 }}>
        {renderStepContent(activeStep)}
        
        <Divider sx={{ my: 3 }} />
        
        <Box display="flex" justifyContent="space-between">
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          <Box>
            {activeStep === steps.length - 1 ? (
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <SaveIcon />}
              >
                Create Course
              </Button>
            ) : (
              <Button
                variant="contained"
                color="primary"
                onClick={handleNext}
              >
                Next
              </Button>
            )}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default CourseCreate; 