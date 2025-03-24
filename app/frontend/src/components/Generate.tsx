import React, { useState } from 'react';
import { 
  Button, 
  TextField, 
  Paper, 
  Typography, 
  CircularProgress,
  Box 
} from '@mui/material';

export default function Generate() {
  const [textbookName, setTextbookName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);

      const response = await fetch('http://localhost:5000/api/generate-deck', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ textbook_name: textbookName }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate deck');
      }

      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3, maxWidth: 600, mx: 'auto', mt: 4 }}>
      <Typography variant="h5" gutterBottom>
        Generate Flashcards
      </Typography>
      
      <Box sx={{ mb: 3 }}>
        <TextField
          fullWidth
          label="Textbook Name"
          value={textbookName}
          onChange={(e) => setTextbookName(e.target.value)}
          disabled={loading}
          placeholder="e.g., Introduction to Python"
          sx={{ mb: 2 }}
        />
        
        <Button
          variant="contained"
          onClick={handleGenerate}
          disabled={!textbookName || loading}
          fullWidth
        >
          {loading ? <CircularProgress size={24} /> : 'Generate Cards'}
        </Button>
      </Box>

      {error && (
        <Typography color="error" sx={{ mt: 2 }}>
          Error: {error}
        </Typography>
      )}

      {result && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="h6" gutterBottom>
            Generation Complete!
          </Typography>
          <Typography>
            Deck ID: {result.deck_id}
          </Typography>
          <Typography>
            Statistics:
          </Typography>
          <ul>
            <li>Parts: {result.statistics.parts}</li>
            <li>Chapters: {result.statistics.chapters}</li>
            <li>Topics: {result.statistics.topics}</li>
            <li>Cards: {result.statistics.cards}</li>
          </ul>
        </Box>
      )}
    </Paper>
  );
} 