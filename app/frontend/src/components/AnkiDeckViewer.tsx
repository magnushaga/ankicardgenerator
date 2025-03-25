import React, { useState } from 'react';
import {
  Box,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  IconButton,
  Divider,
} from '@mui/material';
import FlipIcon from '@mui/icons-material/Flip';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import ClassIcon from '@mui/icons-material/Class';
import TopicIcon from '@mui/icons-material/Topic';

interface AnkiCard {
  id: string;
  front: string;
  back: string;
  partTitle: string;
  chapterTitle: string;
  topicTitle: string;
}

interface Deck {
  id: string;
  title: string;
  cards: AnkiCard[];
}

const AnkiDeckViewer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);

  const searchDecks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`http://localhost:5000/api/search-decks?q=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) throw new Error('Failed to fetch decks');
      const data = await response.json();
      setDecks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleDeckSelect = (deck: Deck) => {
    setSelectedDeck(deck);
    setCurrentCardIndex(0);
    setIsFlipped(false);
  };

  const handleNextCard = () => {
    if (selectedDeck && currentCardIndex < selectedDeck.cards.length - 1) {
      setCurrentCardIndex(prev => prev + 1);
      setIsFlipped(false);
    }
  };

  const handlePreviousCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(prev => prev - 1);
      setIsFlipped(false);
    }
  };

  const handleFlipCard = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <Box sx={{ 
      maxWidth: 1000, 
      margin: 'auto', 
      p: 2,
      bgcolor: '#ffffff',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <Typography variant="h4" gutterBottom sx={{ 
        fontWeight: 300,
        letterSpacing: 1,
        mb: 4
      }}>
        Anki Deck Search
      </Typography>

      <Box sx={{ mb: 6 }}>
        <TextField
          fullWidth
          label="Search decks by title"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && searchDecks()}
          sx={{ 
            mb: 2,
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
          fullWidth
          sx={{ 
            py: 1.5,
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
          Search
        </Button>
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress sx={{ color: '#000000' }} />
        </Box>
      )}

      {error && (
        <Typography sx={{ mb: 2, color: '#000000' }}>
          {error}
        </Typography>
      )}

      {!selectedDeck ? (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {decks.map((deck) => (
            <Card 
              key={deck.id}
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
              onClick={() => handleDeckSelect(deck)}
            >
              <CardContent>
                <Typography variant="h6" sx={{ fontWeight: 400 }}>
                  {deck.title}
                </Typography>
                <Typography sx={{ color: '#666666' }}>
                  {deck.cards.length} cards
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      ) : (
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          <Button 
            onClick={() => setSelectedDeck(null)}
            variant="text"
            startIcon={<NavigateBeforeIcon />}
            sx={{ 
              alignSelf: 'flex-start',
              textTransform: 'none',
              color: '#000000',
              '&:hover': {
                backgroundColor: 'rgba(0, 0, 0, 0.04)'
              }
            }}
          >
            Back to Deck List
          </Button>

          <Typography variant="h5" align="center" sx={{ fontWeight: 300 }}>
            {selectedDeck.title}
          </Typography>

          <Box sx={{ position: 'relative' }}>
            <Card 
              sx={{ 
                minHeight: 500,
                borderRadius: 0,
                boxShadow: 'none',
                border: '1px solid #e0e0e0',
              }}
            >
              <CardContent sx={{ 
                display: 'flex', 
                flexDirection: 'column',
                height: '100%',
                p: 4
              }}>
                {/* Context Information */}
                <Box sx={{ mb: 3 }}>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                    <MenuBookIcon sx={{ color: '#666666' }} />
                    <Typography variant="body2" sx={{ color: '#666666' }}>
                      {selectedDeck.cards[currentCardIndex].partTitle}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1, mb: 1, alignItems: 'center' }}>
                    <ClassIcon sx={{ color: '#666666' }} />
                    <Typography variant="body2" sx={{ color: '#666666' }}>
                      {selectedDeck.cards[currentCardIndex].chapterTitle}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <TopicIcon sx={{ color: '#666666' }} />
                    <Typography variant="body2" sx={{ color: '#666666' }}>
                      {selectedDeck.cards[currentCardIndex].topicTitle}
                    </Typography>
                  </Box>
                </Box>

                <Divider sx={{ mb: 3 }} />

                {/* Card Content */}
                <Box 
                  onClick={handleFlipCard}
                  sx={{ 
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    cursor: 'pointer',
                    p: 4,
                    border: '1px solid #e0e0e0',
                    backgroundColor: '#ffffff',
                    transition: 'background-color 0.2s',
                    '&:hover': {
                      backgroundColor: '#fafafa'
                    }
                  }}
                >
                  <Typography 
                    variant="h6" 
                    align="center"
                    sx={{ fontWeight: 400 }}
                  >
                    {isFlipped 
                      ? selectedDeck.cards[currentCardIndex].back 
                      : selectedDeck.cards[currentCardIndex].front}
                  </Typography>
                </Box>

                <Divider sx={{ mt: 3, mb: 3 }} />

                {/* Navigation Controls */}
                <Box sx={{ 
                  display: 'flex', 
                  justifyContent: 'center', 
                  alignItems: 'center',
                  gap: 3
                }}>
                  <IconButton 
                    onClick={handlePreviousCard}
                    disabled={currentCardIndex === 0}
                    sx={{ 
                      color: '#000000',
                      '&.Mui-disabled': {
                        color: '#cccccc'
                      }
                    }}
                  >
                    <NavigateBeforeIcon />
                  </IconButton>
                  <IconButton 
                    onClick={handleFlipCard}
                    sx={{ color: '#000000' }}
                  >
                    <FlipIcon />
                  </IconButton>
                  <IconButton 
                    onClick={handleNextCard}
                    disabled={currentCardIndex === selectedDeck.cards.length - 1}
                    sx={{ 
                      color: '#000000',
                      '&.Mui-disabled': {
                        color: '#cccccc'
                      }
                    }}
                  >
                    <NavigateNextIcon />
                  </IconButton>
                </Box>

                {/* Card Counter */}
                <Typography 
                  align="center" 
                  sx={{ 
                    mt: 2,
                    color: '#666666',
                    fontSize: '0.9rem'
                  }}
                >
                  {currentCardIndex + 1} / {selectedDeck.cards.length}
                </Typography>
              </CardContent>
            </Card>
          </Box>
        </Box>
      )}

      {/* Add copyright footer */}
      <Box sx={{ 
        mt: 'auto', 
        pt: 4,
        pb: 2,
        borderTop: '1px solid #e0e0e0',
        textAlign: 'center'
      }}>
        <Typography sx={{ 
          color: '#666666',
          fontSize: '0.875rem',
          fontWeight: 300
        }}>
          © {new Date().getFullYear()} Magnus Kobbeltvedt Haga. All rights reserved.
        </Typography>
      </Box>
    </Box>
  );
};

export default AnkiDeckViewer; 