import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Paper,
  Typography,
  Container,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import axios from 'axios';

const DeckSearch = () => {
  const [searchParams, setSearchParams] = useState({
    subject: '',
    textbook_name: '',
  });
  const [decks, setDecks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setSearchParams({
      ...searchParams,
      [e.target.name]: e.target.value,
    });
  };

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.get('http://localhost:53550/api/decks', {
        params: searchParams,
      });
      setDecks(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred while searching decks');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          Search Decks
        </Typography>
        <Box component="form" onSubmit={handleSearch} sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Subject"
            name="subject"
            value={searchParams.subject}
            onChange={handleChange}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Textbook Name"
            name="textbook_name"
            value={searchParams.textbook_name}
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
            {loading ? <CircularProgress size={24} /> : 'Search'}
          </Button>
          {error && (
            <Typography color="error" sx={{ mt: 2 }}>
              {error}
            </Typography>
          )}
        </Box>

        {decks.length > 0 && (
          <List sx={{ mt: 4 }}>
            {decks.map((deck) => (
              <ListItem key={deck.deck_id} divider>
                <ListItemText
                  primary={deck.textbook_name}
                  secondary={`Subject: ${deck.subject} | Parts: ${deck.parts || 'N/A'} | Chapters: ${
                    deck.chapters || 'N/A'
                  }`}
                />
              </ListItem>
            ))}
          </List>
        )}

        {decks.length === 0 && !loading && (
          <Typography sx={{ mt: 4, textAlign: 'center' }}>
            No decks found
          </Typography>
        )}
      </Paper>
    </Container>
  );
};

export default DeckSearch;