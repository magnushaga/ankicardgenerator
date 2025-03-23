import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Container,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

const DeckForm = () => {
  const [formData, setFormData] = useState({
    textbook_name: '',
    parts: '',
    chapters: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      const response = await axios.post('http://localhost:53550/api/decks', formData);
      setSuccess('Deck created successfully!');
      setFormData({
        textbook_name: '',
        subject: '',
        parts: '',
        chapters: '',
      });
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while creating the deck');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Create New Deck
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Textbook Name"
            name="textbook_name"
            value={formData.textbook_name}
            onChange={handleChange}
            required
            margin="normal"
          />
          <TextField
            fullWidth
            label="Subject"
            name="subject"
            value={formData.subject}
            onChange={handleChange}
            required
            margin="normal"
          />
          <TextField
            fullWidth
            label="Parts"
            name="parts"
            value={formData.parts}
            onChange={handleChange}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Chapters"
            name="chapters"
            value={formData.chapters}
            onChange={handleChange}
            margin="normal"
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 3 }}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Create Deck'}
          </Button>
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
          {success && (
            <Typography color="success.main" sx={{ mt: 2 }}>
              {success}
            </Typography>
          )}
        </Box>
      </Paper>
    </Container>
  );
};

export default DeckForm;