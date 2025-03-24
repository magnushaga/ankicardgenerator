import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Card, CardContent, Typography, Button, LinearProgress } from '@mui/material';
import { api } from '../services/api';

export default function StudySession() {
  const { deckId } = useParams();
  const [sessionId, setSessionId] = useState(null);
  const [currentCard, setCurrentCard] = useState(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    startSession();
  }, [deckId]);

  const startSession = async () => {
    const { sessionId } = await api.startStudySession(deckId);
    setSessionId(sessionId);
    await getNextCard(sessionId);
  };

  const getNextCard = async (sid) => {
    setLoading(true);
    setShowAnswer(false);
    const card = await api.getNextCard(deckId, sid);
    setCurrentCard(card);
    setLoading(false);
  };

  const handleRating = async (quality) => {
    await api.submitReview(currentCard.id, sessionId, quality);
    await getNextCard(sessionId);
  };

  if (loading) {
    return <LinearProgress />;
  }

  if (!currentCard) {
    return (
      <Box sx={{ textAlign: 'center', mt: 4 }}>
        <Typography variant="h5">
          No more cards to review!
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            {currentCard.front}
          </Typography>
          
          {showAnswer && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="body1">
                {currentCard.back}
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>

      <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 1 }}>
        {!showAnswer ? (
          <Button variant="contained" onClick={() => setShowAnswer(true)}>
            Show Answer
          </Button>
        ) : (
          <>
            <Button color="error" onClick={() => handleRating(0)}>Again</Button>
            <Button color="warning" onClick={() => handleRating(3)}>Hard</Button>
            <Button color="success" onClick={() => handleRating(4)}>Good</Button>
            <Button color="info" onClick={() => handleRating(5)}>Easy</Button>
          </>
        )}
      </Box>
    </Box>
  );
} 