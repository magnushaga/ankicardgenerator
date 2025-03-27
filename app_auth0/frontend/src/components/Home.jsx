import React from 'react';
import { Container, Typography, Button } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledContainer = styled(Container)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  height: '100vh',
  textAlign: 'center',
}));

const Home = () => {
  return (
    <StyledContainer>
      <Typography variant="h3" gutterBottom>
        Welcome to Auth0 Demo
      </Typography>
      <Button
        variant="contained"
        color="primary"
        onClick={() => window.location.href = '/profile'}
      >
        Go to Profile
      </Button>
    </StyledContainer>
  );
};

export default Home; 