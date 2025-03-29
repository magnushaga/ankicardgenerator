import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Paper,
  Stepper,
  Step,
  StepLabel,
  Divider,
  Fade,
} from '@mui/material';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import NavigateBeforeIcon from '@mui/icons-material/NavigateBefore';
import FlipIcon from '@mui/icons-material/Flip';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNavigate, useLocation } from 'react-router-dom';

const AnkiDeckViewer = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const deck = location.state?.deck;

  const [currentPartIndex, setCurrentPartIndex] = useState(0);
  const [currentChapterIndex, setCurrentChapterIndex] = useState(0);
  const [currentTopicIndex, setCurrentTopicIndex] = useState(0);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [showCard, setShowCard] = useState(true);

  useEffect(() => {
    if (!deck) {
      navigate('/');
    }
  }, [deck, navigate]);

  if (!deck) {
    return null;
  }

  const currentPart = deck.parts[currentPartIndex];
  const currentChapter = currentPart?.chapters[currentChapterIndex];
  const currentTopic = currentChapter?.topics[currentTopicIndex];
  const currentCard = currentTopic?.cards[currentCardIndex];

  const handleNext = () => {
    if (isFlipped) {
      setIsFlipped(false);
      return;
    }

    setShowCard(false);
    setTimeout(() => {
      // Move to next card
      if (currentCardIndex < (currentTopic?.cards.length || 0) - 1) {
        setCurrentCardIndex(currentCardIndex + 1);
        setIsFlipped(false);
        setShowCard(true);
        return;
      }

      // Move to next topic
      if (currentTopicIndex < (currentChapter?.topics.length || 0) - 1) {
        setCurrentTopicIndex(currentTopicIndex + 1);
        setCurrentCardIndex(0);
        setIsFlipped(false);
        setShowCard(true);
        return;
      }

      // Move to next chapter
      if (currentChapterIndex < (currentPart?.chapters.length || 0) - 1) {
        setCurrentChapterIndex(currentChapterIndex + 1);
        setCurrentTopicIndex(0);
        setCurrentCardIndex(0);
        setIsFlipped(false);
        setShowCard(true);
        return;
      }

      // Move to next part
      if (currentPartIndex < (deck.parts.length || 0) - 1) {
        setCurrentPartIndex(currentPartIndex + 1);
        setCurrentChapterIndex(0);
        setCurrentTopicIndex(0);
        setCurrentCardIndex(0);
        setIsFlipped(false);
        setShowCard(true);
        return;
      }
    }, 300);
  };

  const handlePrevious = () => {
    if (isFlipped) {
      setIsFlipped(false);
      return;
    }

    setShowCard(false);
    setTimeout(() => {
      // Move to previous card
      if (currentCardIndex > 0) {
        setCurrentCardIndex(currentCardIndex - 1);
        setIsFlipped(false);
        setShowCard(true);
        return;
      }

      // Move to previous topic
      if (currentTopicIndex > 0) {
        setCurrentTopicIndex(currentTopicIndex - 1);
        setCurrentCardIndex(currentTopic?.cards.length - 1);
        setIsFlipped(false);
        setShowCard(true);
        return;
      }

      // Move to previous chapter
      if (currentChapterIndex > 0) {
        setCurrentChapterIndex(currentChapterIndex - 1);
        setCurrentTopicIndex(currentChapter?.topics.length - 1);
        setCurrentCardIndex(currentTopic?.cards.length - 1);
        setIsFlipped(false);
        setShowCard(true);
        return;
      }

      // Move to previous part
      if (currentPartIndex > 0) {
        setCurrentPartIndex(currentPartIndex - 1);
        setCurrentChapterIndex(currentPart?.chapters.length - 1);
        setCurrentTopicIndex(currentChapter?.topics.length - 1);
        setCurrentCardIndex(currentTopic?.cards.length - 1);
        setIsFlipped(false);
        setShowCard(true);
        return;
      }
    }, 300);
  };

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const getProgressSteps = () => {
    return [
      { label: currentPart?.title || 'Part' },
      { label: currentChapter?.title || 'Chapter' },
      { label: currentTopic?.title || 'Topic' },
      { label: `Card ${currentCardIndex + 1}/${currentTopic?.cards.length || 0}` }
    ];
  };

  return (
    <Box sx={{ 
      maxWidth: 800, 
      margin: 'auto', 
      p: 4,
      display: 'flex',
      flexDirection: 'column',
      gap: 4
    }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <IconButton onClick={() => navigate('/')}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h5" sx={{ flex: 1 }}>
          {deck.title}
        </Typography>
      </Box>

      <Stepper activeStep={3} alternativeLabel>
        {getProgressSteps().map((step, index) => (
          <Step key={index}>
            <StepLabel>{step.label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Divider />

      <Fade in={showCard} timeout={300}>
        <Box>
          {currentCard && (
            <Card 
              sx={{ 
                minHeight: 300,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                cursor: 'pointer',
                transition: 'transform 0.3s',
                transform: isFlipped ? 'rotateY(180deg)' : 'none',
                '&:hover': {
                  boxShadow: 6
                }
              }}
              onClick={handleFlip}
            >
              <CardContent sx={{ textAlign: 'center' }}>
                <Typography variant="h6" gutterBottom>
                  {isFlipped ? 'Answer' : 'Question'}
                </Typography>
                <Typography variant="body1">
                  {isFlipped ? currentCard.back : currentCard.front}
                </Typography>
              </CardContent>
            </Card>
          )}
        </Box>
      </Fade>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        <Button
          variant="outlined"
          startIcon={<NavigateBeforeIcon />}
          onClick={handlePrevious}
          disabled={currentPartIndex === 0 && currentChapterIndex === 0 && 
                   currentTopicIndex === 0 && currentCardIndex === 0}
        >
          Previous
        </Button>
        <Button
          variant="outlined"
          startIcon={<FlipIcon />}
          onClick={handleFlip}
        >
          Flip
        </Button>
        <Button
          variant="outlined"
          endIcon={<NavigateNextIcon />}
          onClick={handleNext}
          disabled={currentPartIndex === deck.parts.length - 1 && 
                   currentChapterIndex === currentPart?.chapters.length - 1 && 
                   currentTopicIndex === currentChapter?.topics.length - 1 && 
                   currentCardIndex === currentTopic?.cards.length - 1}
        >
          Next
        </Button>
      </Box>
    </Box>
  );
};

export default AnkiDeckViewer; 