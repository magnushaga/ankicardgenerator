import React from 'react';
import { 
  Box, 
  Typography, 
  Button, 
  Grid, 
  Card, 
  CardContent,
  useTheme,
  Container
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
        <Grid container spacing={4} sx={{ mb: { xs: 6, md: 8 } }}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card 
                sx={{ 
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  textAlign: 'center',
                  p: 2,
                  transition: 'transform 0.2s',
                  '&:hover': {
                    transform: 'translateY(-4px)'
                  }
                }}
              >
                <Box sx={{ 
                  color: 'primary.main',
                  mb: 2
                }}>
                  {feature.icon}
                </Box>
                <CardContent>
                  <Typography 
                    variant="h6" 
                    component="h3" 
                    sx={{ mb: 1 }}
                  >
                    {feature.title}
                  </Typography>
                  <Typography 
                    variant="body2" 
                    color="text.secondary"
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