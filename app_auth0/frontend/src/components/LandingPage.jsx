import React from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Card, 
  CardContent,
  useTheme,
  Container,
  Grid
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useTheme as useCustomTheme } from '../lib/ThemeContext';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import SchoolIcon from '@mui/icons-material/School';
import TimelineIcon from '@mui/icons-material/Timeline';
import GroupIcon from '@mui/icons-material/Group';

const LandingPage = () => {
  const theme = useTheme();
  const { isDarkMode } = useCustomTheme();
  const navigate = useNavigate();

  const features = [
    {
      icon: <AutoAwesomeIcon sx={{ fontSize: 40 }} />,
      title: 'Smart Card Generation',
      description: 'AI-powered flashcard creation from your study materials'
    },
    {
      icon: <SchoolIcon sx={{ fontSize: 40 }} />,
      title: 'Organized Learning',
      description: 'Structured study materials with hierarchical organization'
    },
    {
      icon: <TimelineIcon sx={{ fontSize: 40 }} />,
      title: 'Progress Tracking',
      description: 'Monitor your learning journey with detailed analytics'
    },
    {
      icon: <GroupIcon sx={{ fontSize: 40 }} />,
      title: 'Collaborative Learning',
      description: 'Share and study with peers in study groups'
    }
  ];

  return (
    <Box sx={{ 
      minHeight: '100vh',
      bgcolor: 'background.default',
      pt: { xs: 4, md: 8 }
    }}>
      {/* Hero Section */}
      <Container maxWidth="lg">
        <Box sx={{ 
          textAlign: 'center',
          mb: { xs: 6, md: 8 }
        }}>
          <Typography 
            variant="h1" 
            component="h1" 
            sx={{ 
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              fontWeight: 700,
              mb: 2,
              background: `linear-gradient(45deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
              backgroundClip: 'text',
              textFillColor: 'transparent'
            }}
          >
            StudIQ
          </Typography>
          <Typography 
            variant="h5" 
            sx={{ 
              mb: 4,
              color: 'text.secondary',
              maxWidth: '800px',
              mx: 'auto'
            }}
          >
            Transform your study materials into powerful flashcards with AI
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
            <Button 
              variant="contained" 
              size="large"
              onClick={() => navigate('/login')}
              sx={{ 
                px: 4,
                py: 1.5,
                borderRadius: 2
              }}
            >
              Get Started
            </Button>
            <Button 
              variant="outlined" 
              size="large"
              onClick={() => navigate('/about')}
              sx={{ 
                px: 4,
                py: 1.5,
                borderRadius: 2
              }}
            >
              Learn More
            </Button>
          </Box>
        </Box>

        {/* Features Section */}
        <Grid 
          container 
          spacing={{ xs: 3, md: 4 }} 
          sx={{ 
            mb: { xs: 6, md: 8 },
            px: { xs: 2, sm: 3, md: 4 }
          }}
        >
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
            sx={{ mb: 2 }}
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
            onClick={() => navigate('/login')}
            sx={{ 
              px: 6,
              py: 1.5,
              borderRadius: 2
            }}
          >
            Start Free Trial
          </Button>
        </Box>
      </Container>
    </Box>
  );
};

export default LandingPage; 