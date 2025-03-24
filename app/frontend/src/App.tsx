import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Box, AppBar, Toolbar, Button, Typography, Container } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import Generate from './pages/Generate';
import Search from './pages/Search';

function App() {
  return (
    <BrowserRouter>
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              AnkiCards
            </Typography>
            <Button 
              color="inherit" 
              component={RouterLink} 
              to="/search"
            >
              Search
            </Button>
            <Button 
              color="inherit" 
              component={RouterLink} 
              to="/generate"
            >
              Generate
            </Button>
          </Toolbar>
        </AppBar>
        <Container>
          <Routes>
            <Route path="/generate" element={<Generate />} />
            <Route path="/search" element={<Search />} />
            <Route path="/" element={<Search />} />
          </Routes>
        </Container>
      </Box>
    </BrowserRouter>
  );
}

export default App; 