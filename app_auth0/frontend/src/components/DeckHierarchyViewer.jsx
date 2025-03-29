import React, { useState } from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Collapse,
  IconButton,
  Paper,
  Divider,
} from '@mui/material';
import ExpandLess from '@mui/icons-material/ExpandLess';
import ExpandMore from '@mui/icons-material/ExpandMore';
import MenuBookIcon from '@mui/icons-material/MenuBook';
import ClassIcon from '@mui/icons-material/Class';
import TopicIcon from '@mui/icons-material/Topic';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import { useNavigate } from 'react-router-dom';

const DeckHierarchyViewer = ({ deck }) => {
  const navigate = useNavigate();
  const [expandedParts, setExpandedParts] = useState({});
  const [expandedChapters, setExpandedChapters] = useState({});

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

  const handleStartDeck = () => {
    navigate(`/deck/${deck.id}/view`, { state: { deck } });
  };

  return (
    <Box sx={{ maxWidth: 800, margin: 'auto', p: 4 }}>
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h4" component="h1">
            {deck.title}
          </Typography>
          <IconButton 
            onClick={handleStartDeck}
            color="primary"
            sx={{ 
              backgroundColor: 'primary.main',
              color: 'white',
              '&:hover': {
                backgroundColor: 'primary.dark'
              }
            }}
          >
            <NavigateNextIcon />
          </IconButton>
        </Box>
        <Divider sx={{ mb: 3 }} />
        
        <List component="nav">
          {deck.parts.map((part) => (
            <React.Fragment key={part.id}>
              <ListItem 
                button 
                onClick={() => togglePart(part.id)}
                sx={{ 
                  backgroundColor: 'background.paper',
                  mb: 1,
                  borderRadius: 1
                }}
              >
                <ListItemIcon>
                  <MenuBookIcon color="primary" />
                </ListItemIcon>
                <ListItemText 
                  primary={part.title}
                  secondary={`${part.chapters.length} chapters`}
                />
                {expandedParts[part.id] ? <ExpandLess /> : <ExpandMore />}
              </ListItem>
              
              <Collapse in={expandedParts[part.id]} timeout="auto" unmountOnExit>
                <List component="div" disablePadding>
                  {part.chapters.map((chapter) => (
                    <React.Fragment key={chapter.id}>
                      <ListItem 
                        button 
                        onClick={() => toggleChapter(chapter.id)}
                        sx={{ pl: 4, backgroundColor: 'background.paper', mb: 1, borderRadius: 1 }}
                      >
                        <ListItemIcon>
                          <ClassIcon color="secondary" />
                        </ListItemIcon>
                        <ListItemText 
                          primary={chapter.title}
                          secondary={`${chapter.topics.length} topics`}
                        />
                        {expandedChapters[chapter.id] ? <ExpandLess /> : <ExpandMore />}
                      </ListItem>
                      
                      <Collapse in={expandedChapters[chapter.id]} timeout="auto" unmountOnExit>
                        <List component="div" disablePadding>
                          {chapter.topics.map((topic) => (
                            <ListItem 
                              key={topic.id}
                              sx={{ 
                                pl: 6, 
                                backgroundColor: 'background.paper', 
                                mb: 1, 
                                borderRadius: 1 
                              }}
                            >
                              <ListItemIcon>
                                <TopicIcon color="action" />
                              </ListItemIcon>
                              <ListItemText 
                                primary={topic.title}
                                secondary={`${topic.cards.length} cards`}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Collapse>
                    </React.Fragment>
                  ))}
                </List>
              </Collapse>
            </React.Fragment>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default DeckHierarchyViewer; 