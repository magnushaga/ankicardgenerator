import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Grid,
  TextField,
  Button,
  Alert,
  Paper,
} from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';

const DeckSearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [decks, setDecks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const searchDecks = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get the access token from session storage
      const accessToken = sessionStorage.getItem('access_token');
      if (!accessToken) {
        setError('Please log in to search decks');
        return;
      }

      const response = await fetch(`http://localhost:5002/api/search-decks?q=${encodeURIComponent(searchQuery)}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 401) {
          setError('Please log in again');
          // Clear the token and redirect to login
          sessionStorage.removeItem('access_token');
          localStorage.removeItem('user_info');
          localStorage.removeItem('tokens');
          window.location.href = '/';
          return;
        }
        throw new Error(errorData.error || 'Failed to fetch decks');
      }
      
      const data = await response.json();
      setDecks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setDecks([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      searchDecks();
    }
  };

  const accessToken = sessionStorage.getItem('access_token');

  if (!accessToken) {
    return (
      <Box sx={{ 
        maxWidth: 1000, 
        margin: 'auto', 
        p: 2,
        bgcolor: '#ffffff',
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Paper 
          elevation={0}
          sx={{ 
            p: 4, 
            textAlign: 'center',
            maxWidth: 400,
            width: '100%'
          }}
        >
          <MenuBookIcon sx={{ fontSize: 48, color: '#666666', mb: 2 }} />
          <Typography variant="h5" sx={{ mb: 2, color: '#333333' }}>
            Welcome to Anki Card Generator
          </Typography>
          <Typography sx={{ mb: 3, color: '#666666' }}>
            Please log in to search and create decks
          </Typography>
          <Button
            variant="outlined"
            onClick={() => navigate('/')}
            sx={{ 
              py: 1.5,
              px: 3,
              borderRadius: 0,
              textTransform: 'none',
              fontSize: '1.1rem',
              borderColor: '#000000',
              color: '#000000',
              '&:hover': {
                borderColor: '#000000',
                backgroundColor: 'rgba(0, 0, 0, 0.04)'
              }
            }}
          >
            Go to Login
          </Button>
        </Paper>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      maxWidth: 1000, 
      margin: 'auto', 
      p: 2,
      bgcolor: '#ffffff',
      minHeight: '100vh'
    }}>
      {/* Search Bar */}
      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        mb: 4,
        alignItems: 'center'
      }}>
        <TextField
          fullWidth
          label="Search decks by title"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          sx={{ 
            '& .MuiOutlinedInput-root': {
              borderRadius: 0,
              borderColor: '#000000'
            },
            '& .MuiOutlinedInput-root:hover .MuiOutlinedInput-notchedOutline': {
              borderColor: '#000000'
            },
            '& .MuiOutlinedInput-root.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#000000'
            },
            '& .MuiInputLabel-root.Mui-focused': {
              color: '#000000'
            }
          }}
        />
        <Button
          variant="outlined"
          onClick={searchDecks}
          disabled={loading}
          startIcon={<SearchIcon />}
          sx={{ 
            py: 1.5,
            px: 3,
            borderRadius: 0,
            textTransform: 'none',
            fontSize: '1.1rem',
            borderColor: '#000000',
            color: '#000000',
            '&:hover': {
              borderColor: '#000000',
              backgroundColor: 'rgba(0, 0, 0, 0.04)'
            }
          }}
        >
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </Box>

      {/* Error Message */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Loading Spinner */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress sx={{ color: '#000000' }} />
        </Box>
      )}

      {/* Results Grid */}
      <Grid container spacing={2}>
        {decks.map((deck) => (
          <Grid item xs={12} sm={6} md={4} key={deck.id}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                borderRadius: 0,
                border: '1px solid #e0e0e0',
                boxShadow: 'none',
                transition: 'all 0.2s',
                '&:hover': { 
                  backgroundColor: '#f5f5f5',
                  transform: 'translateX(4px)'
                }
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <MenuBookIcon sx={{ color: '#666666' }} />
                  <Typography variant="h6" sx={{ fontWeight: 400 }}>
                    {deck.title}
                  </Typography>
                </Box>
                <Typography sx={{ color: '#666666' }}>
                  {deck.cards?.length || 0} cards
                </Typography>
                {deck.cards && deck.cards.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Sample cards:
                    </Typography>
                    {deck.cards.slice(0, 2).map((card, index) => (
                      <Typography 
                        key={index}
                        sx={{ 
                          color: '#666666',
                          fontSize: '0.875rem',
                          mt: 0.5
                        }}
                      >
                        • {card.front}
                      </Typography>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* No Results Message */}
      {!loading && decks.length === 0 && !error && (
        <Box sx={{ 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          py: 8
        }}>
          <MenuBookIcon sx={{ fontSize: 48, color: '#666666', mb: 2 }} />
          <Typography sx={{ color: '#666666' }}>
            No decks found. Try searching for something else.
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default DeckSearch; 