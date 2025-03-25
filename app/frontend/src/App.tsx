import React from 'react';
import { Box } from '@mui/material';
import AnkiDeckViewer from './components/AnkiDeckViewer';

function App() {
  return (
    <Box sx={{ 
      width: '100%',
      minHeight: '100vh',
      bgcolor: '#fafafa'
    }}>
      <AnkiDeckViewer />
    </Box>
  );
}

export default App;
