import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  List,
  ListItem,
  ListItemText,
  Collapse,
  CircularProgress
} from '@mui/material';
import { FiChevronDown, FiChevronRight } from 'react-icons/fi';

interface Topic {
  id: number;
  title: string;
}

interface Chapter {
  id: number;
  title: string;
  topics: Topic[];
}

interface Part {
  id: number;
  title: string;
  chapters: Chapter[];
}

interface DeckStructure {
  id: number;
  name: string;
  parts: Part[];
}

interface DeckExplorerProps {
  deckId: number;
}

const DeckExplorer: React.FC<DeckExplorerProps> = ({ deckId }) => {
  const [structure, setStructure] = useState<DeckStructure | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedParts, setExpandedParts] = useState<number[]>([]);
  const [expandedChapters, setExpandedChapters] = useState<number[]>([]);

  useEffect(() => {
    const fetchDeckStructure = async () => {
      try {
        const response = await fetch(`/api/deck-structure/${deckId}`);
        if (!response.ok) throw new Error('Failed to fetch deck structure');
        const data = await response.json();
        setStructure(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchDeckStructure();
  }, [deckId]);

  const togglePart = (partId: number) => {
    setExpandedParts(prev => 
      prev.includes(partId) 
        ? prev.filter(id => id !== partId)
        : [...prev, partId]
    );
  };

  const toggleChapter = (chapterId: number) => {
    setExpandedChapters(prev => 
      prev.includes(chapterId) 
        ? prev.filter(id => id !== chapterId)
        : [...prev, chapterId]
    );
  };

  if (loading) return <CircularProgress />;
  if (error) return <Typography color="error">{error}</Typography>;
  if (!structure) return <Typography>No structure found</Typography>;

  return (
    <Paper elevation={0} sx={{ p: 2, bgcolor: '#fafafa' }}>
      <Typography variant="h5" sx={{ mb: 3 }}>
        {structure.name}
      </Typography>
      
      <List>
        {structure.parts.map((part) => (
          <Box key={part.id} sx={{ mb: 2 }}>
            <Button
              fullWidth
              onClick={() => togglePart(part.id)}
              sx={{
                justifyContent: 'flex-start',
                textAlign: 'left',
                bgcolor: '#fff',
                mb: 1,
                gap: 1
              }}
            >
              {expandedParts.includes(part.id) ? 
                <FiChevronDown size={20} /> : 
                <FiChevronRight size={20} />
              }
              <Typography variant="subtitle1">
                {part.title}
              </Typography>
            </Button>
            
            <Collapse in={expandedParts.includes(part.id)}>
              <List sx={{ pl: 2 }}>
                {part.chapters.map((chapter) => (
                  <Box key={chapter.id} sx={{ mb: 1 }}>
                    <Button
                      fullWidth
                      onClick={() => toggleChapter(chapter.id)}
                      sx={{
                        justifyContent: 'flex-start',
                        textAlign: 'left',
                        bgcolor: '#f5f5f5'
                      }}
                    >
                      <Typography variant="body1">
                        {expandedChapters.includes(chapter.id) ? <FiChevronDown /> : <FiChevronRight />} {chapter.title}
                      </Typography>
                    </Button>
                    
                    <Collapse in={expandedChapters.includes(chapter.id)}>
                      <List sx={{ pl: 3 }}>
                        {chapter.topics.map((topic) => (
                          <ListItem key={topic.id}>
                            <ListItemText 
                              primary={topic.title}
                              sx={{ 
                                '& .MuiTypography-root': { 
                                  fontSize: '0.9rem',
                                  color: 'text.secondary'
                                }
                              }}
                            />
                          </ListItem>
                        ))}
                      </List>
                    </Collapse>
                  </Box>
                ))}
              </List>
            </Collapse>
          </Box>
        ))}
      </List>
    </Paper>
  );
};

export default DeckExplorer; 