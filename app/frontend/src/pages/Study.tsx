import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Box, Typography, CircularProgress } from '@mui/material';
import { api } from '../services/api';
import StudyCard from '../components/StudyCard';

export default function Study() {
  const { deckId } = useParams<{ deckId: string }>();
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentCard, setCurrentCard] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    startSession();
  }, [deckId]);

  const startSession = async () => {
    if (!deckId) return;
    try {
      const { sessionId } = await api.startStudySession(deckId);
      setSessionId(sessionId);
      await getNextCard(sessionId);
    } catch (error) {
      console.error('Failed to start session:', error);
    }
  };

  const getNextCard = async (sid: string) => {
    if (!deckId) return;
    try {
      setLoading(true);
      const card = await api.getNextCard(deckId, sid);
      setCurrentCard(card);
    } catch (error) {
      console.error('Failed to get next card:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRate = async (rating: number) => {
    if (!sessionId || !currentCard) return;
    try {
      await api.submitReview(currentCard.id, sessionId, rating);
      await getNextCard(sessionId);
    } catch (error) {
      console.error('Failed to submit review:', error);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!currentCard) {
    return (
      <Typography variant="h5" sx={{ textAlign: 'center', mt: 4 }}>
        No more cards to review!
      </Typography>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      <StudyCard
        front={currentCard.front}
        back={currentCard.back}
        onRate={handleRate}
      />
    </Box>
  );
} 