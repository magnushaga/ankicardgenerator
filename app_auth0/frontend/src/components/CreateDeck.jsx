import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Container,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useCustomTheme } from '../hooks/useCustomTheme';
import { useAuth } from '../hooks/useAuth';

const steps = ['Enter Textbook Name', 'Generating Deck', 'Complete'];

const CreateDeck = () => {
  const [textbookName, setTextbookName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeStep, setActiveStep] = useState(0);
  const navigate = useNavigate();
  const { theme } = useCustomTheme();
  const { getAccessToken } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setActiveStep(1);

    try {
      const token = await getAccessToken();
      const response = await fetch('/api/generate-deck', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({ textbook_name: textbookName }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to generate deck');
      }

      const data = await response.json();
      setActiveStep(2);
      
      // Navigate to the new deck after a short delay
      setTimeout(() => {
        navigate(`/deck/${data.deck.id}`);
      }, 1500);

    } catch (err) {
      setError(err.message);
      setActiveStep(0);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Create New Deck
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" align="center" gutterBottom>
          Enter a textbook name to generate a structured deck of flashcards
        </Typography>
      </Box>

      <Paper 
        elevation={3} 
        sx={{ 
          p: 4, 
          display: 'flex', 
          flexDirection: 'column',
          alignItems: 'center',
          background: theme.palette.background.paper,
        }}
      >
        <Stepper activeStep={activeStep} sx={{ width: '100%', mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ width: '100%', mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} sx={{ width: '100%' }}>
          <TextField
            fullWidth
            label="Textbook Name"
            variant="outlined"
            value={textbookName}
            onChange={(e) => setTextbookName(e.target.value)}
            disabled={loading}
            required
            sx={{ mb: 3 }}
          />

          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Button
              type="submit"
              variant="contained"
              size="large"
              disabled={loading || !textbookName.trim()}
              sx={{ minWidth: 200 }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Generate Deck'
              )}
            </Button>
          </Box>
        </Box>

        {activeStep === 2 && (
          <Box sx={{ mt: 3, textAlign: 'center' }}>
            <Typography variant="h6" color="success.main">
              Deck Generated Successfully!
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Redirecting to your new deck...
            </Typography>
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default CreateDeck; 