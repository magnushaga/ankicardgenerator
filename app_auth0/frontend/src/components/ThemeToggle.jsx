import React from 'react';
import IconButton from '@mui/material/IconButton';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { useTheme } from '../lib/ThemeContext';

export const ThemeToggle = () => {
  const { isDarkMode, toggleTheme } = useTheme();

  return (
    <IconButton
      onClick={toggleTheme}
      color="inherit"
      aria-label="toggle theme"
      sx={{
        position: 'fixed',
        bottom: 16,
        right: 16,
        zIndex: 1000,
        backgroundColor: 'background.paper',
        '&:hover': {
          backgroundColor: 'action.hover',
        },
      }}
    >
      {isDarkMode ? <Brightness7Icon /> : <Brightness4Icon />}
    </IconButton>
  );
}; 