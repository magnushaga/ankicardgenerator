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
  Paper,
} from '@mui/material';
import FlipIcon from '@mui/icons-material/Flip';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';

interface DeckCard {
  id: string;
  front: string;
  back: string;
}

interface Topic {
  id: string;
  title: string;
  cards: DeckCard[];
}

interface Chapter {
  id: string;
  title: string;
  topics: Topic[];
}

interface Part {
  id: string;
  title: string;
  chapters: Chapter[];
}

interface Deck {
  id: string;
  title: string;
  parts: Part[];
}

const DeckViewer: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [decks, setDecks] = useState<Deck[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDeck, setSelectedDeck] = useState<Deck | null>(null);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [allCards, setAllCards] = useState<DeckCard[]>([]);

  const searchDecks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`http://localhost:5000/api/search-decks?q=${encodeURIComponent(searchQuery)}`);
      if (!response.ok) {
        throw new Error('Failed to fetch decks');
      }
      const data = await response.json();
      setDecks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const selectDeck = (deck: Deck) => {
    setSelectedDeck(deck);
    // Flatten all cards from the deck structure
    const cards: DeckCard[] = [];
    deck.parts.forEach(part => {
      part.chapters.forEach(chapter => {
        chapter.topics.forEach(topic => {
          cards.push(...topic.cards);
        });
      });
    });
    setAllCards(cards);
    setCurrentCardIndex(0);
    setIsFlipped(false);
  };

  const nextCard = () => {
    if (currentCardIndex < allCards.length - 1) {
      setCurrentCardIndex(prev => prev + 1);
      setIsFlipped(false);
    }
  };

  const previousCard = () => {
    if (currentCardIndex > 0) {
      setCurrentCardIndex(prev => prev - 1);
      setIsFlipped(false);
    }
  };

  const flipCard = () => {
    setIsFlipped(!isFlipped);
  };

  return (
    <Box sx={{ maxWidth: 800, margin: 'auto', p: 2 }}>
      <Typography variant="h4" gutterBottom>
        Deck Search
      </Typography>

      <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
        <TextField
          fullWidth
          label="Search decks by title"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && searchDecks()}
        />
        <Button
          variant="contained"
          onClick={searchDecks}
          disabled={loading}
        >
          Search
        </Button>
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}

      {!selectedDeck ? (
        // Show deck list
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {decks.map((deck) => (
            <Card 
              key={deck.id} 
              sx={{ cursor: 'pointer' }}
              onClick={() => selectDeck(deck)}
            >
              <CardContent>
                <Typography variant="h6">{deck.title}</Typography>
                <Typography color="textSecondary">
                  {deck.parts.length} parts
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      ) : (
        // Show card viewer
        <Box>
          <Button 
            onClick={() => setSelectedDeck(null)}
            sx={{ mb: 2 }}
          >
            ← Back to Deck List
          </Button>

          <Typography variant="h5" gutterBottom>
            {selectedDeck.title}
          </Typography>

          {allCards.length > 0 && (
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
              <Paper
                elevation={3}
                sx={{
                  width: '100%',
                  height: 300,
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  cursor: 'pointer',
                  p: 2,
                  backgroundColor: '#f5f5f5',
                }}
                onClick={flipCard}
              >
                <Typography variant="h6" align="center">
                  {isFlipped 
                    ? allCards[currentCardIndex].back 
                    : allCards[currentCardIndex].front}
                </Typography>
              </Paper>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <IconButton 
                  onClick={previousCard}
                  disabled={currentCardIndex === 0}
                >
                  <NavigateBeforeIcon />
                </IconButton>
                <IconButton onClick={flipCard}>
                  <FlipIcon />
                </IconButton>
                <IconButton 
                  onClick={nextCard}
                  disabled={currentCardIndex === allCards.length - 1}
                >
                  <NavigateNextIcon />
                </IconButton>
              </Box>

              <Typography>
                Card {currentCardIndex + 1} of {allCards.length}
              </Typography>
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};

export default DeckViewer; 