import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  CircularProgress
} from '@mui/material';

const DeckManager: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const handleSearch = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/analyze-textbook', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ textbook_name: searchQuery }),
      });

      if (!response.ok) throw new Error('Failed to search');
      const data = await response.json();
      // Ensure parts array exists and is an array
      if (!Array.isArray(data.parts)) {
        console.warn('Deck data missing parts array:', data);
        data.parts = [];
      }
      data.parts = data.parts.map((part: any) => ({
        id: part.id || '',
        title: part.title || 'Untitled Part',
        chapters: Array.isArray(part.chapters) ? part.chapters.map((chapter: any) => ({
          id: chapter.id || '',
          title: chapter.title || 'Untitled Chapter',
          topics: Array.isArray(chapter.topics) ? chapter.topics.map((topic: any) => ({
            id: topic.id || '',
            title: topic.title || 'Untitled Topic',
            cards: Array.isArray(topic.cards) ? topic.cards : []
          })) : []
        })) : []
      }));
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Paper elevation={1} sx={{ p: 2, mb: 3 }}>
        <TextField
          fullWidth
          label="Enter Textbook Name"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          sx={{ mb: 2 }}
        />
        <Button 
          variant="contained"
          onClick={handleSearch}
          disabled={loading || !searchQuery.trim()}
        >
          Search
        </Button>
      </Paper>

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {result && (
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Search Results
          </Typography>
          <pre style={{ whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Paper>
      )}
    </Box>
  );
};

export default DeckManager; 