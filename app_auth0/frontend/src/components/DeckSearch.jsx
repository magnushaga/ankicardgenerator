import React, { useState, useEffect } from 'react';
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
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import SearchIcon from '@mui/icons-material/Search';
import { useNavigate } from 'react-router-dom';

const DeckSearch = ({ userInfo: propUserInfo, accessToken: propAccessToken }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [decks, setDecks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userInfo, setUserInfo] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Check authentication state on component mount
    const checkAuth = async () => {
      console.log('Checking authentication state:');
      console.log('Access Token:', propAccessToken ? propAccessToken.substring(0, 20) + '...' : 'Not found');
      console.log('User Info:', propUserInfo || 'Not found');
      
      if (propAccessToken && propUserInfo) {
        setIsAuthenticated(true);
        setUserInfo(propUserInfo);
        
        // Verify token is still valid
        try {
          console.log('Verifying token with Auth0...');
          const response = await fetch('http://localhost:5001/userinfo', {
            headers: {
              'Authorization': `Bearer ${propAccessToken}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (!response.ok) {
            console.error('Token verification failed:', response.status, response.statusText);
            throw new Error('Token verification failed');
          }
          
          const data = await response.json();
          console.log('Token verification successful:', data);
          setUserInfo(data.user);
        } catch (err) {
          console.error('Token verification error:', err);
          // Clear invalid session
          localStorage.removeItem('access_token');
          localStorage.removeItem('user_info');
          localStorage.removeItem('tokens');
          setIsAuthenticated(false);
          setUserInfo(null);
          navigate('/');
        }
      } else {
        console.log('No authentication found, redirecting to login');
        setIsAuthenticated(false);
        setUserInfo(null);
      }
    };

    checkAuth();
  }, [navigate, propAccessToken, propUserInfo]);

  const searchDecks = async () => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setError(null);

    try {
      console.log('Searching decks with query:', searchQuery);
      console.log('Using access token:', propAccessToken ? propAccessToken.substring(0, 20) + '...' : 'Not found');

      const response = await fetch(`http://localhost:5002/api/search-decks?q=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'Authorization': `Bearer ${propAccessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to search decks');
      }

      const data = await response.json();
      console.log('Search results:', data);
      setDecks(data);
    } catch (err) {
      console.error('Search error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeckSelect = async (deck) => {
    try {
      console.log('Navigating to deck view:', deck.id);
      
      // Navigate to the deck viewer with the deck ID
      navigate(`/deck/${deck.id}/cards`);
    } catch (err) {
      console.error('Error navigating to deck view:', err);
      setError(err.message);
    }
  };

  if (!isAuthenticated) {
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
      maxWidth: 800, 
      margin: 'auto', 
      p: 4,
      display: 'flex',
      flexDirection: 'column',
      gap: 4
    }}>
      <Box sx={{ display: 'flex', gap: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search decks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && searchDecks()}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 0,
              '&:hover fieldset': {
                borderColor: '#000000',
              },
            },
          }}
        />
        <Button
          variant="outlined"
          onClick={searchDecks}
          disabled={loading || !searchQuery.trim()}
          sx={{
            borderRadius: 0,
            borderColor: '#000000',
            color: '#000000',
            '&:hover': {
              borderColor: '#000000',
              backgroundColor: 'rgba(0, 0, 0, 0.04)',
            },
          }}
        >
          {loading ? <CircularProgress size={24} /> : 'Search'}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ borderRadius: 0 }}>
          {error}
        </Alert>
      )}

      <List sx={{ width: '100%' }}>
        {decks.map((deck) => (
          <ListItem
            key={deck.id}
            button
            onClick={() => handleDeckSelect(deck)}
            sx={{
              border: '1px solid #e0e0e0',
              mb: 2,
              '&:hover': {
                backgroundColor: '#f5f5f5',
              },
            }}
          >
            <ListItemText
              primary={deck.title}
              secondary={`Created: ${new Date(deck.created_at).toLocaleDateString()}`}
            />
          </ListItem>
        ))}
      </List>

      {!loading && decks.length === 0 && searchQuery && (
        <Typography align="center" color="text.secondary">
          No decks found matching your search.
        </Typography>
      )}
    </Box>
  );
};

export default DeckSearch; 