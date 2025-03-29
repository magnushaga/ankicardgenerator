import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Grid,
  Button,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  Divider,
  IconButton,
  Collapse,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import { useParams } from 'react-router-dom';

const DeckViewer = () => {
  const { deckId } = useParams();
  const [deck, setDeck] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedParts, setExpandedParts] = useState({});
  const [expandedChapters, setExpandedChapters] = useState({});
  const [expandedTopics, setExpandedTopics] = useState({});

  useEffect(() => {
    const fetchDeck = async () => {
      try {
        const accessToken = sessionStorage.getItem('access_token');
        const response = await fetch(`http://localhost:5002/api/decks/${deckId}/cards`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error || 'Failed to fetch deck');
        }

        const data = await response.json();
        setDeck(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDeck();
  }, [deckId]);

  const togglePart = (partId) => {
    setExpandedParts(prev => ({
      ...prev,
      [partId]: !prev[partId]
    }));
  };

  const toggleChapter = (chapterId) => {
    setExpandedChapters(prev => ({
      ...prev,
      [chapterId]: !prev[chapterId]
    }));
  };

  const toggleTopic = (topicId) => {
    setExpandedTopics(prev => ({
      ...prev,
      [topicId]: !prev[topicId]
    }));
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  if (!deck) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">No deck found</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3, maxWidth: 1200, margin: 'auto' }}>
      <Typography variant="h4" sx={{ mb: 4 }}>
        {deck.title}
      </Typography>

      {deck.parts.map((part) => (
        <Paper key={part.id} sx={{ mb: 3, p: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ flex: 1 }}>
              {part.title}
            </Typography>
            <IconButton onClick={() => togglePart(part.id)}>
              {expandedParts[part.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>

          <Collapse in={expandedParts[part.id]}>
            {part.chapters.map((chapter) => (
              <Box key={chapter.id} sx={{ ml: 2, mb: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle1" sx={{ flex: 1 }}>
                    {chapter.title}
                  </Typography>
                  <IconButton onClick={() => toggleChapter(chapter.id)}>
                    {expandedChapters[chapter.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                  </IconButton>
                </Box>

                <Collapse in={expandedChapters[chapter.id]}>
                  {chapter.topics.map((topic) => (
                    <Box key={topic.id} sx={{ ml: 2, mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body1" sx={{ flex: 1 }}>
                          {topic.title}
                        </Typography>
                        <IconButton onClick={() => toggleTopic(topic.id)}>
                          {expandedTopics[topic.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                        </IconButton>
                      </Box>

                      <Collapse in={expandedTopics[topic.id]}>
                        <Grid container spacing={2}>
                          {topic.cards.map((card) => (
                            <Grid item xs={12} md={6} key={card.id}>
                              <Card variant="outlined">
                                <CardContent>
                                  <Typography variant="h6" gutterBottom>
                                    Question:
                                  </Typography>
                                  <Typography paragraph>
                                    {card.front}
                                  </Typography>
                                  <Divider sx={{ my: 2 }} />
                                  <Typography variant="h6" gutterBottom>
                                    Answer:
                                  </Typography>
                                  <Typography>
                                    {card.back}
                                  </Typography>
                                </CardContent>
                              </Card>
                            </Grid>
                          ))}
                        </Grid>
                      </Collapse>
                    </Box>
                  ))}
                </Collapse>
              </Box>
            ))}
          </Collapse>
        </Paper>
      ))}
    </Box>
  );
};

export default DeckViewer; 