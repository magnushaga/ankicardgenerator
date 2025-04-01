import React from 'react';
import { Container, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import CreateDeckButton from './CreateDeckButton';
import DeckSearch from './DeckSearch';

const StyledContainer = styled(Container)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  paddingTop: theme.spacing(4),
  minHeight: '100vh',
  textAlign: 'center',
}));

const Home = () => {
  return (
    <StyledContainer>
      <Typography variant="h3" gutterBottom>
        Welcome to StudIQ
      </Typography>
      <Typography variant="h6" color="text.secondary" paragraph>
        Create and study your flashcards
      </Typography>
      
      <Box sx={{ width: '100%', maxWidth: 600, mt: 4 }}>
        <CreateDeckButton />
        <DeckSearch />
      </Box>
    </StyledContainer>
  );
};

export default Home; 