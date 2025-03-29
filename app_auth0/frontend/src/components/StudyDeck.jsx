import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  LinearProgress,
  Rating,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import FlipIcon from '@mui/icons-material/Flip';
import CloseIcon from '@mui/icons-material/Close';

const StudyDeck = () => {
  const { deckId } = useParams();
  const navigate = useNavigate();
  const [cards, setCards] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showEndDialog, setShowEndDialog] = useState(false);
  const [startTime, setStartTime] = useState(null);
  const [sessionStats, setSessionStats] = useState(null);

  useEffect(() => {
    const startStudySession = async () => {
      try {
        const accessToken = sessionStorage.getItem('access_token');
        
        // Create study session
        const sessionResponse = await fetch('http://localhost:5002/api/study-sessions', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ deck_id: deckId }),
        });

        if (!sessionResponse.ok) {
          throw new Error('Failed to create study session');
        }

        const sessionData = await sessionResponse.json();
        setSessionId(sessionData.sessionId);
        setStartTime(Date.now());

        // Fetch due cards
        const cardsResponse = await fetch(`http://localhost:5002/api/decks/${deckId}/due-cards`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });

        if (!cardsResponse.ok) {
          throw new Error('Failed to fetch cards');
        }

        const cardsData = await cardsResponse.json();
        setCards(cardsData);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    startStudySession();
  }, [deckId]);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleRating = async (quality) => {
    try {
      const accessToken = sessionStorage.getItem('access_token');
      const timeTaken = Date.now() - startTime;

      // Record the review
      const response = await fetch('http://localhost:5002/api/review-card', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          card_id: cards[currentCardIndex].id,
          session_id: sessionId,
          quality,
          time_taken: timeTaken,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to record review');
      }

      // Move to next card
      if (currentCardIndex < cards.length - 1) {
        setCurrentCardIndex(currentCardIndex + 1);
        setIsFlipped(false);
        setStartTime(Date.now());
      } else {
        // End session if no more cards
        await endStudySession();
        setShowEndDialog(true);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const endStudySession = async () => {
    try {
      const accessToken = sessionStorage.getItem('access_token');
      
      const response = await fetch(`http://localhost:5002/api/study-sessions/${sessionId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to end study session');
      }

      const stats = await response.json();
      setSessionStats(stats.statistics);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleEndSession = () => {
    setShowEndDialog(false);
    navigate(`/deck/${deckId}/cards`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error">{error}</Typography>
        <Button onClick={() => navigate(`/deck/${deckId}/cards`)}>
          Return to Deck
        </Button>
      </Box>
    );
  }

  if (cards.length === 0) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h6">No cards due for review!</Typography>
        <Button onClick={() => navigate(`/deck/${deckId}/cards`)}>
          Return to Deck
        </Button>
      </Box>
    );
  }

  const currentCard = cards[currentCardIndex];
  const progress = ((currentCardIndex + 1) / cards.length) * 100;

  return (
    <Box sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">
          Card {currentCardIndex + 1} of {cards.length}
        </Typography>
        <IconButton onClick={() => setShowEndDialog(true)}>
          <CloseIcon />
        </IconButton>
      </Box>

      <LinearProgress variant="determinate" value={progress} sx={{ mb: 3 }} />

      <Card 
        sx={{ 
          minHeight: 300,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          cursor: 'pointer',
          position: 'relative',
          transform: isFlipped ? 'rotateY(180deg)' : 'none',
          transition: 'transform 0.6s',
          transformStyle: 'preserve-3d',
        }}
        onClick={handleFlip}
      >
        <CardContent sx={{ textAlign: 'center' }}>
          <Typography variant="h5" component="div">
            {isFlipped ? currentCard.back : currentCard.front}
          </Typography>
          {!isFlipped && (
            <Box sx={{ mt: 2 }}>
              <IconButton onClick={handleFlip}>
                <FlipIcon />
              </IconButton>
            </Box>
          )}
        </CardContent>
      </Card>

      {isFlipped && (
        <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Rating
            value={0}
            onChange={(_, value) => handleRating(value)}
            max={5}
            size="large"
          />
        </Box>
      )}

      <Dialog open={showEndDialog} onClose={() => setShowEndDialog(false)}>
        <DialogTitle>End Study Session</DialogTitle>
        <DialogContent>
          {sessionStats && (
            <Box sx={{ mt: 2 }}>
              <Typography>Cards Studied: {sessionStats.totalCards}</Typography>
              <Typography>Average Quality: {sessionStats.averageQuality.toFixed(1)}</Typography>
              <Typography>Total Time: {(sessionStats.totalTimeMs / 1000).toFixed(1)}s</Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEndDialog(false)}>Continue Studying</Button>
          <Button onClick={handleEndSession} variant="contained">
            End Session
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default StudyDeck; 