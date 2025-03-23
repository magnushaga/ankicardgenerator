import { Box, Container, Typography, Button, Grid, Paper } from '@mui/material';
import { AutoStories, Psychology, School } from '@mui/icons-material';
import Link from 'next/link';

export default function Home() {
  return (
    <>
      {/* Hero Section */}
      <Box
        sx={{
          pt: 8,
          pb: 12,
          background: 'linear-gradient(45deg, #9c27b0 30%, #e91e63 90%)',
          color: 'white',
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography
                variant="h1"
                sx={{
                  fontSize: { xs: '2.5rem', md: '3.5rem' },
                  fontWeight: 700,
                  mb: 2,
                }}
              >
                Transform Your Learning with AI-Powered Flashcards
              </Typography>
              <Typography variant="h5" sx={{ mb: 4, opacity: 0.9 }}>
                Generate smart Anki cards from any textbook and master your subjects faster
              </Typography>
              <Button
                component={Link}
                href="/generate"
                variant="contained"
                size="large"
                sx={{
                  bgcolor: 'white',
                  color: 'primary.main',
                  '&:hover': {
                    bgcolor: 'grey.100',
                  },
                  mr: 2,
                }}
              >
                Get Started
              </Button>
              <Button
                component={Link}
                href="/explore"
                variant="outlined"
                size="large"
                sx={{
                  color: 'white',
                  borderColor: 'white',
                  '&:hover': {
                    borderColor: 'grey.100',
                    bgcolor: 'rgba(255,255,255,0.1)',
                  },
                }}
              >
                Explore Decks
              </Button>
            </Grid>
            <Grid item xs={12} md={6}>
              {/* Add hero image or animation here */}
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ py: 8 }}>
        <Grid container spacing={4}>
          <Grid item xs={12} md={4}>
            <Paper
              elevation={0}
              sx={{
                p: 4,
                height: '100%',
                bgcolor: 'background.paper',
                borderRadius: 2,
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <AutoStories sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h2" gutterBottom>
                Smart Generation
              </Typography>
              <Typography color="text.secondary">
                Upload your textbook and let our AI create optimized flashcards tailored to your learning needs.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper
              elevation={0}
              sx={{
                p: 4,
                height: '100%',
                bgcolor: 'background.paper',
                borderRadius: 2,
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <Psychology sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h2" gutterBottom>
                Spaced Repetition
              </Typography>
              <Typography color="text.secondary">
                Study efficiently with our implementation of the SuperMemo algorithm for optimal retention.
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={4}>
            <Paper
              elevation={0}
              sx={{
                p: 4,
                height: '100%',
                bgcolor: 'background.paper',
                borderRadius: 2,
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                },
              }}
            >
              <School sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
              <Typography variant="h5" component="h2" gutterBottom>
                Track Progress
              </Typography>
              <Typography color="text.secondary">
                Monitor your learning journey with detailed statistics and performance insights.
              </Typography>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </>
  );
}