import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  CircularProgress,
  List,
  ListItem,
  Collapse
} from '@mui/material';

const StructureView: React.FC = () => {
  const { textbookName } = useParams();
  const [structure, setStructure] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStructure = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/generate-textbook-structure', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ textbook_name: textbookName }),
        });

        if (!response.ok) throw new Error('Failed to generate structure');
        const data = await response.json();
        setStructure(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    if (textbookName) {
      fetchStructure();
    }
  }, [textbookName]);

  const renderPart = (part: any) => (
    <Paper key={part.id} elevation={1} sx={{ mb: 2, p: 2 }}>
      <Typography variant="h6" sx={{ mb: 1 }}>
        {part.title}
      </Typography>
      <List>
        {part.chapters?.map((chapter: any) => (
          <ListItem 
            key={chapter.id} 
            sx={{ 
              flexDirection: 'column', 
              alignItems: 'flex-start',
              pl: 2 
            }}
          >
            <Typography variant="subtitle1">
              {chapter.title}
            </Typography>
            <List sx={{ pl: 2, width: '100%' }}>
              {chapter.topics?.map((topic: any) => (
                <ListItem key={topic.id}>
                  <Typography variant="body2">
                    • {topic.title}
                  </Typography>
                </ListItem>
              ))}
            </List>
          </ListItem>
        ))}
      </List>
    </Paper>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error" sx={{ p: 4, textAlign: 'center' }}>
        {error}
      </Typography>
    );
  }

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Structure for: {textbookName}
      </Typography>
      {structure?.parts?.map(renderPart)}
    </Box>
  );
};

export default StructureView; 