import React from 'react';
import { Container, CssBaseline, Box, Typography, AppBar, Toolbar } from '@mui/material';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import DeckForm from './components/DeckForm';
import DeckSearch from './components/DeckSearch';

const theme = createTheme();

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div">
            Anki Card Generator
          </Typography>
        </Toolbar>
      </AppBar>
      <Container>
        <Box sx={{ mt: 4 }}>
          <DeckForm />
          <Box sx={{ my: 4 }}>
            <DeckSearch />
          </Box>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
