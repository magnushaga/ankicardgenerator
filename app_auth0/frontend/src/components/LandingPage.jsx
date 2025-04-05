import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent,
  useTheme,
  Container,
  Grid,
  Tabs,
  Tab,
  Paper,
  TextField,
  InputAdornment,
  Chip,
  Divider,
  Avatar,
  Badge,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  AppBar,
  Toolbar,
  Link
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useTheme as useCustomTheme } from '../lib/ThemeContext';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SchoolIcon from '@mui/icons-material/School';
import BookIcon from '@mui/icons-material/Book';
import LibraryBooksIcon from '@mui/icons-material/LibraryBooks';
import CreateIcon from '@mui/icons-material/Create';
import HistoryIcon from '@mui/icons-material/History';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import NotificationsIcon from '@mui/icons-material/Notifications';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import EditNoteIcon from '@mui/icons-material/EditNote';
import PsychologyIcon from '@mui/icons-material/Psychology';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ImportContactsIcon from '@mui/icons-material/ImportContacts';
import MenuIcon from '@mui/icons-material/Menu';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import LoginButton from './LoginButton';

const LandingPage = ({ userInfo, isAdmin, onLogout }) => {
  const theme = useTheme();
  const { isDarkMode, toggleTheme } = useCustomTheme();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterAnchorEl, setFilterAnchorEl] = useState(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState(null);
  const [selectedSubject, setSelectedSubject] = useState('all');
  const [userMenuAnchorEl, setUserMenuAnchorEl] = useState(null);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleFilterClick = (event) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleMenuClick = (event) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleUserMenuClick = (event) => {
    setUserMenuAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setFilterAnchorEl(null);
    setMenuAnchorEl(null);
    setUserMenuAnchorEl(null);
  };

  const handleSubjectSelect = (subject) => {
    setSelectedSubject(subject);
    handleClose();
  };

  const handleProfile = () => {
    handleClose();
    navigate('/profile');
  };

  const handleAdminPanel = () => {
    handleClose();
    navigate('/admin');
  };

  const handleLogout = () => {
    handleClose();
    onLogout();
  };

  const subjects = [
    { id: 'all', label: 'All Subjects' },
    { id: 'computer-science', label: 'Computer Science' },
    { id: 'mathematics', label: 'Mathematics' },
    { id: 'physics', label: 'Physics' },
    { id: 'biology', label: 'Biology' },
    { id: 'chemistry', label: 'Chemistry' },
    { id: 'history', label: 'History' },
    { id: 'literature', label: 'Literature' }
  ];

  const features = [
    {
      icon: <AutoAwesomeIcon sx={{ fontSize: 40 }} />,
      title: 'AI-Powered Card Generation',
      description: 'Transform your study materials into effective flashcards with our advanced AI'
    },
    {
      icon: <EditNoteIcon sx={{ fontSize: 40 }} />,
      title: 'Notion-Like Editor',
      description: 'Create rich, structured notes with our TipTap-powered editor'
    },
    {
      icon: <PsychologyIcon sx={{ fontSize: 40 }} />,
      title: 'Spaced Repetition',
      description: 'Optimize your learning with Anki-compatible spaced repetition algorithms'
    },
    {
      icon: <HistoryIcon sx={{ fontSize: 40 }} />,
      title: 'Progress Analytics',
      description: 'Track your learning journey with detailed analytics and insights'
    }
  ];

  const mainActions = [
    {
      icon: <SchoolIcon sx={{ fontSize: 40 }} />,
      title: 'Courses',
      description: 'Browse and enroll in courses',
      action: () => navigate('/courses')
    },
    {
      icon: <BookIcon sx={{ fontSize: 40 }} />,
      title: 'Textbooks',
      description: 'Find and import textbooks',
      action: () => navigate('/textbooks')
    },
    {
      icon: <CreateIcon sx={{ fontSize: 40 }} />,
      title: 'Create Deck',
      description: 'Create a new flashcard deck',
      action: () => navigate('/create-deck')
    },
    {
      icon: <LibraryBooksIcon sx={{ fontSize: 40 }} />,
      title: 'My Decks',
      description: 'View and manage your decks',
      action: () => navigate('/dashboard')
    }
  ];

  const quickActions = [
    {
      icon: <ImportContactsIcon />,
      title: 'Import Textbook',
      description: 'Upload a PDF or EPUB file',
      action: () => navigate('/textbooks')
    },
    {
      icon: <CloudUploadIcon />,
      title: 'Import Anki Deck',
      description: 'Import your existing Anki decks',
      action: () => navigate('/import-anki')
    },
    {
      icon: <EditNoteIcon />,
      title: 'Create Note',
      description: 'Create a new note with our editor',
      action: () => navigate('/create-note')
    },
    {
      icon: <SchoolIcon />,
      title: 'Enroll in University',
      description: 'Connect with educational institutions',
      action: () => navigate('/universities')
    }
  ];

  return (
    <Box sx={{ 
      minHeight: '100vh',
      bgcolor: 'background.default'
    }}>
      <Container maxWidth="lg" sx={{ pt: { xs: 2, md: 4 } }}>
        {/* Hero Section */}
        <Box sx={{ 
          textAlign: 'center',
          py: { xs: 4, md: 8 },
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center'
        }}>
          <Typography 
            variant="h1" 
            component="h1" 
            sx={{ 
              fontSize: { xs: '2.5rem', md: '4rem' },
              fontWeight: 800,
              mb: 2,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text',
              textFillColor: 'transparent',
              maxWidth: '800px'
            }}
          >
            Your AI-Powered Study Companion
          </Typography>
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 4,
              color: 'text.secondary',
              maxWidth: '800px',
              mx: 'auto',
              fontWeight: 400
            }}
          >
            Transform textbooks, notes, and courses into effective flashcards with AI. 
            Compatible with Anki and featuring a Notion-like editor.
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button 
              variant="contained" 
              size="large"
              onClick={() => navigate('/signup')}
              sx={{ 
                px: 4,
                py: 1.5,
                borderRadius: 2,
                textTransform: 'none',
                fontSize: '1.1rem'
              }}
            >
              Get Started Free
            </Button>
            <Button 
              variant="outlined" 
              size="large"
              onClick={() => navigate('/demo')}
              sx={{ 
                px: 4,
                py: 1.5,
                borderRadius: 2,
                textTransform: 'none',
                fontSize: '1.1rem'
              }}
            >
              Watch Demo
            </Button>
          </Box>
          
          {/* Subject Filter */}
          <Box sx={{ mt: 4, display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
            {subjects.map((subject) => (
              <Chip
                key={subject.id}
                label={subject.label}
                onClick={() => setSelectedSubject(subject.id)}
                color={selectedSubject === subject.id ? 'primary' : 'default'}
                sx={{ 
                  borderRadius: 2,
                  '&:hover': {
                    bgcolor: selectedSubject === subject.id 
                      ? theme.palette.primary.main 
                      : theme.palette.action.hover
                  }
                }}
              />
            ))}
          </Box>
        </Box>

        {/* Quick Actions */}
        <Box sx={{ my: { xs: 4, md: 6 } }}>
          <Typography variant="h4" component="h2" fontWeight={700} sx={{ mb: 3 }}>
            Quick Actions
          </Typography>
          <Grid container spacing={3}>
            {quickActions.map((action, index) => (
              <Grid xs={12} sm={6} md={3} key={index}>
                <Paper
                  sx={{
                    p: 3,
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    cursor: 'pointer',
                    '&:hover': {
                      transform: 'translateY(-5px)',
                      boxShadow: 6
                    }
                  }}
                  onClick={action.action}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar
                      sx={{
                        bgcolor: 'primary.main',
                        color: 'primary.contrastText',
                        mr: 2
                      }}
                    >
                      {action.icon}
                    </Avatar>
                    <Typography variant="h6" component="h3" fontWeight={600}>
                      {action.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {action.description}
                  </Typography>
                  <Box sx={{ mt: 'auto', display: 'flex', justifyContent: 'flex-end' }}>
                    <IconButton size="small" color="primary">
                      <ArrowForwardIcon />
                    </IconButton>
                  </Box>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Box>

        {/* Features Section */}
        <Box sx={{ mb: { xs: 6, md: 8 } }}>
          <Typography variant="h5" component="h2" sx={{ mb: 3, fontWeight: 600 }}>
            Powerful Features
          </Typography>
          <Grid container spacing={3}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card 
                sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 3,
                  transition: 'all 0.3s ease-in-out',
                  bgcolor: isDarkMode ? 'background.paper' : 'background.default',
                  border: `1px solid ${theme.palette.divider}`,
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: theme.shadows[8],
                    borderColor: theme.palette.primary.main
                  }
                }}
              >
                <Box sx={{ 
                  color: 'primary.main',
                  mb: 2,
                  p: 2,
                  borderRadius: '50%',
                  bgcolor: isDarkMode ? 'rgba(25, 118, 210, 0.1)' : 'rgba(25, 118, 210, 0.05)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  {feature.icon}
                </Box>
                <CardContent sx={{ flexGrow: 1, p: 2 }}>
                  <Typography 
                    variant="h6" 
                    component="h3" 
                    sx={{ 
                      mb: 1,
                      fontWeight: 600,
                      color: 'text.primary'
                    }}
                  >
                    {feature.title}
                  </Typography>
                  <Typography 
                    variant="body1" 
                    color="text.secondary"
                    sx={{ 
                      lineHeight: 1.6,
                      fontSize: '0.95rem'
                    }}
                  >
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        </Box>

        {/* Anki Integration */}
        <Box 
          sx={{ 
            mb: { xs: 6, md: 8 },
            p: 4,
            borderRadius: 4,
            bgcolor: isDarkMode ? 'background.paper' : 'grey.50',
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            alignItems: 'center',
            gap: 4
          }}
        >
          <Box sx={{ flex: 1 }}>
            <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 600 }}>
              Seamless Anki Integration
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Import your existing Anki decks or export your StudIQ decks to Anki. 
              Our spaced repetition algorithm is compatible with Anki's SuperMemo 2 algorithm.
            </Typography>
            <Button 
              variant="outlined" 
              endIcon={<ArrowForwardIcon />}
              onClick={() => navigate('/anki-integration')}
              sx={{ 
                borderRadius: 2,
                textTransform: 'none'
              }}
            >
              Learn More About Anki Integration
            </Button>
          </Box>
          <Box 
            sx={{ 
              width: { xs: '100%', md: '40%' },
              height: '300px',
              bgcolor: isDarkMode ? 'background.default' : 'background.paper',
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: `1px solid ${theme.palette.divider}`
            }}
          >
            {/* Placeholder for Anki integration image */}
            <Typography variant="h6" color="text.secondary">
              Anki Integration Visualization
            </Typography>
          </Box>
        </Box>

        {/* Notion-like Editor */}
        <Box 
          sx={{ 
            mb: { xs: 6, md: 8 },
            p: 4,
            borderRadius: 4,
            bgcolor: isDarkMode ? 'background.paper' : 'grey.50',
            display: 'flex',
            flexDirection: { xs: 'column-reverse', md: 'row' },
            alignItems: 'center',
            gap: 4
          }}
        >
          <Box 
            sx={{ 
              width: { xs: '100%', md: '40%' },
              height: '300px',
              bgcolor: isDarkMode ? 'background.default' : 'background.paper',
              borderRadius: 2,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: `1px solid ${theme.palette.divider}`
            }}
          >
            {/* Placeholder for TipTap editor image */}
            <Typography variant="h6" color="text.secondary">
              TipTap Editor Visualization
            </Typography>
          </Box>
          <Box sx={{ flex: 1 }}>
            <Typography variant="h5" component="h2" sx={{ mb: 2, fontWeight: 600 }}>
              Notion-Like Editor with TipTap
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              Create rich, structured notes with our TipTap-powered editor. 
              Organize your knowledge with blocks, tables, and more. 
              Convert your notes to flashcards with a single click.
            </Typography>
            <Button 
              variant="outlined" 
              endIcon={<ArrowForwardIcon />}
              onClick={() => navigate('/editor')}
              sx={{ 
                borderRadius: 2,
                textTransform: 'none'
              }}
            >
              Try Our Editor
            </Button>
          </Box>
        </Box>

        {/* CTA Section */}
        <Box 
          sx={{ 
            textAlign: 'center',
            bgcolor: isDarkMode ? 'background.paper' : 'grey.50',
            borderRadius: 4,
            p: { xs: 4, md: 6 },
            mb: { xs: 4, md: 6 }
          }}
        >
          <Typography 
            variant="h4" 
            component="h2" 
            sx={{ mb: 2, fontWeight: 700 }}
          >
            Ready to Transform Your Learning?
          </Typography>
          <Typography 
            variant="body1" 
            sx={{ 
              mb: 4,
              color: 'text.secondary',
              maxWidth: '600px',
              mx: 'auto'
            }}
          >
            Join thousands of students who are already using StudIQ to create better flashcards and study more effectively.
          </Typography>
          <Button 
            variant="contained" 
            size="large"
            onClick={() => navigate('/signup')}
            sx={{ 
              px: 6,
              py: 1.5,
              borderRadius: 2,
              textTransform: 'none',
              fontSize: '1.1rem'
            }}
          >
            Start Free Trial
          </Button>
        </Box>
      </Container>

      {/* Footer */}
      <Box 
        component="footer" 
        sx={{ 
          mt: 8, 
          pb: 8,
          borderTop: 1,
          borderColor: 'divider',
          pt: 6
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4}>
            <Grid xs={12} sm={6} md={3}>
              <Typography variant="h6" gutterBottom>
                StudIQ
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI-powered study tools for students and educators.
              </Typography>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Product
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {['Features', 'Pricing', 'Integrations', 'Updates'].map((item) => (
                  <Typography 
                    key={item} 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}
                  >
                    {item}
                  </Typography>
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Resources
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {['Documentation', 'Tutorials', 'Blog', 'Support'].map((item) => (
                  <Typography 
                    key={item} 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}
                  >
                    {item}
                  </Typography>
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                Company
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                {['About', 'Careers', 'Contact', 'Legal'].map((item) => (
                  <Typography 
                    key={item} 
                    variant="body2" 
                    color="text.secondary"
                    sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}
                  >
                    {item}
                  </Typography>
                ))}
              </Box>
            </Grid>
          </Grid>
          <Divider sx={{ my: 4 }} />
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
            <Typography variant="body2" color="text.secondary">
              © 2024 StudIQ. All rights reserved.
            </Typography>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                Privacy Policy
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ cursor: 'pointer', '&:hover': { color: 'primary.main' } }}>
                Terms of Service
              </Typography>
            </Box>
          </Box>
        </Container>
      </Box>

      {/* Filter Menu */}
      <Menu
        anchorEl={filterAnchorEl}
        open={Boolean(filterAnchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: { minWidth: 200, borderRadius: 2 }
        }}
      >
        <MenuItem onClick={() => handleSubjectSelect('all')}>
          <ListItemText primary="All Subjects" />
        </MenuItem>
        <Divider />
        {subjects.filter(s => s.id !== 'all').map((subject) => (
          <MenuItem key={subject.id} onClick={() => handleSubjectSelect(subject.id)}>
            <ListItemText primary={subject.label} />
          </MenuItem>
        ))}
      </Menu>

      {/* Mobile Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleClose}
        PaperProps={{
          sx: { minWidth: 200, borderRadius: 2 }
        }}
      >
        {['Courses', 'Textbooks', 'Universities', 'Pricing'].map((item) => (
          <MenuItem key={item} onClick={handleClose}>
            <ListItemText primary={item} />
          </MenuItem>
        ))}
        <Divider />
        <MenuItem onClick={handleClose}>
          <ListItemIcon>
            <AccountCircleIcon fontSize="small" />
          </ListItemIcon>
          <ListItemText primary="Sign In" />
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default LandingPage; 