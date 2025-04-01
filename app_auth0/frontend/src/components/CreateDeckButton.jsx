import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Box } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { useCustomTheme } from '../hooks/useCustomTheme';

const CreateDeckButton = () => {
  const navigate = useNavigate();
  const { theme } = useCustomTheme();

  const handleClick = () => {
    navigate('/create-deck');
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
      <Button
        variant="contained"
        color="primary"
        startIcon={<AddIcon />}
        onClick={handleClick}
        sx={{
          borderRadius: 2,
          textTransform: 'none',
          px: 4,
          py: 1.5,
          fontSize: '1.1rem',
          boxShadow: theme.shadows[2],
          '&:hover': {
            boxShadow: theme.shadows[4],
            transform: 'translateY(-1px)',
          },
        }}
      >
        Create New Deck
      </Button>
    </Box>
  );
};

export default CreateDeckButton; 