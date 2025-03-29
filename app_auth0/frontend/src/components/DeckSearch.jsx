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
          sessionStorage.removeItem('access_token');
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
    try {
      setLoading(true);
      setError(null);
      
      // Log all available information about the token and user
      console.log('=== Search Request Debug Info ===');
      console.log('Prop Access Token:', propAccessToken ? propAccessToken.substring(0, 20) + '...' : 'Not found');
      console.log('Prop User Info:', propUserInfo);
      console.log('Local User Info:', userInfo);
      console.log('Is Authenticated:', isAuthenticated);
      console.log('Session Storage Token:', sessionStorage.getItem('access_token')?.substring(0, 20) + '...');
      console.log('Local Storage User Info:', localStorage.getItem('user_info'));
      console.log('================================');
      
      if (!propAccessToken) {
        console.error('No access token found in props');
        setError('Please log in to search decks');
        return;
      }
      
      // Create headers object with authorization
      const headers = {
        'Authorization': `Bearer ${propAccessToken}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      };
      
      console.log('Request headers:', headers);
      
      const url = `http://localhost:5002/api/search-decks?q=${encodeURIComponent(searchQuery)}`;
      console.log('Request URL:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: headers,
        credentials: 'include'  // Include credentials if using cookies
      });
      
      console.log('Response status:', response.status);
      console.log('Response headers:', Object.fromEntries(response.headers.entries()));
      
      if (!response.ok) {
        const errorData = await response.json();
        console.error('Search request failed:', {
          status: response.status,
          statusText: response.statusText,
          error: errorData,
          headers: Object.fromEntries(response.headers.entries())
        });
        
        if (response.status === 401) {
          // Handle authentication errors
          if (errorData.error === "Token has expired") {
            console.log('Token expired, clearing session');
            setError('Your session has expired. Please log in again.');
            sessionStorage.removeItem('access_token');
            localStorage.removeItem('user_info');
            localStorage.removeItem('tokens');
            setIsAuthenticated(false);
            setUserInfo(null);
            navigate('/');
            return;
          }
          setError('Authentication error. Please try again.');
          return;
        }
        throw new Error(errorData.error || 'Failed to fetch decks');
      }
      
      const data = await response.json();
      console.log('Search response:', data);
      setDecks(data);
    } catch (err) {
      console.error('Search error:', err);
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
      maxWidth: 1000, 
      margin: 'auto', 
      p: 2,
      bgcolor: '#ffffff',
      minHeight: '100vh'
    }}>
      {/* Welcome Message */}
      {userInfo && (
        <Typography variant="h6" sx={{ mb: 3, color: '#333333' }}>
          Welcome, {userInfo.email}!
        </Typography>
      )}

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