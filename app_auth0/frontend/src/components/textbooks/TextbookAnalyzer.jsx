import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Paper,
  useTheme,
  Divider,
  Chip
} from '@mui/material';
import { useParams, useNavigate } from 'react-router-dom';
import { useTheme as useCustomTheme } from '../../lib/ThemeContext';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';

const steps = ['Select Content', 'Generate Cards', 'Review & Save'];

const TextbookAnalyzer = () => {
  const theme = useTheme();
  const { isDarkMode } = useCustomTheme();
  const { id } = useParams();
  const navigate = useNavigate();
  const [activeStep, setActiveStep] = useState(0);
  const [textbook, setTextbook] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedChapters, setSelectedChapters] = useState([]);
  const [generatedCards, setGeneratedCards] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    // TODO: Fetch textbook details from backend
    setTextbook({
      id: id,
      title: 'Introduction to Computer Science',
      author: 'John Smith',
      chapters: [
        { id: 1, title: 'Introduction to Programming', pages: '1-50' },
        { id: 2, title: 'Data Types and Variables', pages: '51-100' },
        { id: 3, title: 'Control Structures', pages: '101-150' },
        { id: 4, title: 'Functions and Modules', pages: '151-200' }
      ]
    });
  }, [id]);

  const handleChapterSelect = (chapterId) => {
    setSelectedChapters(prev => {
      if (prev.includes(chapterId)) {
        return prev.filter(id => id !== chapterId);
      }
      return [...prev, chapterId];
    });
  };

  const handleGenerateCards = async () => {
    setLoading(true);
    setError(null);
    try {
      // TODO: Implement card generation API call
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulated API call
      setGeneratedCards([
        {
          id: 1,
          question: 'What is a variable in programming?',
          answer: 'A variable is a storage location paired with an associated symbolic name, which contains some known or unknown quantity of data or object.',
          chapter: 'Data Types and Variables'
        },
        {
          id: 2,
          question: 'What are the basic control structures in programming?',
          answer: 'The basic control structures are sequence, selection (if-else), and iteration (loops).',
          chapter: 'Control Structures'
        }
      ]);
      setActiveStep(2);
    } catch (err) {
      setError('Failed to generate cards. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCards = async () => {
    setLoading(true);
    try {
      // TODO: Implement save cards API call
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulated API call
      navigate('/dashboard');
    } catch (err) {
      setError('Failed to save cards. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Select Chapters to Analyze
            </Typography>
            <Grid container spacing={2}>
              {textbook?.chapters.map((chapter) => (
                <Grid item xs={12} sm={6} md={4} key={chapter.id}>
                  <Card
                    sx={{
                      cursor: 'pointer',
                      bgcolor: selectedChapters.includes(chapter.id)
                        ? isDarkMode
                          ? 'rgba(25, 118, 210, 0.1)'
                          : 'rgba(25, 118, 210, 0.05)'
                        : 'background.paper',
                      border: `1px solid ${
                        selectedChapters.includes(chapter.id)
                          ? theme.palette.primary.main
                          : theme.palette.divider
                      }`,
                      '&:hover': {
                        borderColor: theme.palette.primary.main
                      }
                    }}
                    onClick={() => handleChapterSelect(chapter.id)}
                  >
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {chapter.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Pages: {chapter.pages}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>
        );

      case 1:
        return (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            {loading ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                <CircularProgress size={60} sx={{ mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  Generating Flashcards...
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  This may take a few minutes
                </Typography>
              </Box>
            ) : (
              <Button
                variant="contained"
                size="large"
                startIcon={<AutoAwesomeIcon />}
                onClick={handleGenerateCards}
                disabled={selectedChapters.length === 0}
              >
                Generate Flashcards
              </Button>
            )}
          </Box>
        );

      case 2:
        return (
          <Box>
            <Typography variant="h6" gutterBottom>
              Review Generated Cards
            </Typography>
            <Grid container spacing={2}>
              {generatedCards.map((card) => (
                <Grid item xs={12} key={card.id}>
                  <Paper
                    sx={{
                      p: 2,
                      bgcolor: isDarkMode ? 'background.paper' : 'background.default'
                    }}
                  >
                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={card.chapter}
                        size="small"
                        sx={{ mr: 1 }}
                      />
                    </Box>
                    <Typography variant="subtitle1" gutterBottom>
                      Q: {card.question}
                    </Typography>
                    <Divider sx={{ my: 1 }} />
                    <Typography variant="body1" color="text.secondary">
                      A: {card.answer}
                    </Typography>
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </Box>
        );

      default:
        return null;
    }
  };

  if (!textbook) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {textbook.title}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          by {textbook.author}
        </Typography>
      </Box>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {error && (
        <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', color: 'error.main' }}>
          <ErrorIcon sx={{ mr: 1 }} />
          <Typography>{error}</Typography>
        </Box>
      )}

      {renderStepContent(activeStep)}

      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'space-between' }}>
        <Button
          disabled={activeStep === 0}
          onClick={() => setActiveStep((prev) => prev - 1)}
        >
          Back
        </Button>
        {activeStep === 0 && (
          <Button
            variant="contained"
            onClick={() => setActiveStep((prev) => prev + 1)}
            disabled={selectedChapters.length === 0}
          >
            Next
          </Button>
        )}
        {activeStep === 2 && (
          <Button
            variant="contained"
            onClick={handleSaveCards}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} /> : <CheckCircleIcon />}
          >
            Save Cards
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default TextbookAnalyzer; 