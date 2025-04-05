import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  useTheme,
  Paper
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import { useTheme as useCustomTheme } from '../../lib/ThemeContext';

const TextbookDashboard = () => {
  const theme = useTheme();
  const { isDarkMode } = useCustomTheme();
  const navigate = useNavigate();
  const [textbooks, setTextbooks] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [newTextbook, setNewTextbook] = useState({
    title: '',
    author: '',
    description: ''
  });

  useEffect(() => {
    // TODO: Fetch textbooks from backend
    // This is a placeholder for demonstration
    setTextbooks([
      {
        id: 1,
        title: 'Introduction to Computer Science',
        author: 'John Smith',
        description: 'A comprehensive guide to computer science fundamentals',
        createdAt: '2024-03-15'
      },
      {
        id: 2,
        title: 'Data Structures and Algorithms',
        author: 'Jane Doe',
        description: 'Advanced concepts in data structures and algorithms',
        createdAt: '2024-03-10'
      }
    ]);
  }, []);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleCreateTextbook = () => {
    // TODO: Implement textbook creation with file upload
    setOpenDialog(false);
    setNewTextbook({ title: '', author: '', description: '' });
    setSelectedFile(null);
  };

  const handleDeleteTextbook = (id) => {
    // TODO: Implement textbook deletion
    setTextbooks(textbooks.filter(textbook => textbook.id !== id));
  };

  const handleAnalyzeTextbook = (id) => {
    // TODO: Navigate to textbook analysis page
    navigate(`/textbooks/analyze/${id}`);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
        <Typography variant="h4" component="h1">
          My Textbooks
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenDialog(true)}
        >
          Add Textbook
        </Button>
      </Box>

      <Grid container spacing={3}>
        {textbooks.map((textbook) => (
          <Grid item xs={12} sm={6} md={4} key={textbook.id}>
            <Card
              sx={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                transition: 'all 0.3s ease-in-out',
                bgcolor: isDarkMode ? 'background.paper' : 'background.default',
                border: `1px solid ${theme.palette.divider}`,
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[4],
                  borderColor: theme.palette.primary.main
                }
              }}
            >
              <CardContent sx={{ flexGrow: 1 }}>
                <Typography variant="h6" component="h2" gutterBottom>
                  {textbook.title}
                </Typography>
                <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                  by {textbook.author}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {textbook.description}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Added on {new Date(textbook.createdAt).toLocaleDateString()}
                </Typography>
              </CardContent>
              <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between' }}>
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => handleAnalyzeTextbook(textbook.id)}
                >
                  Analyze
                </Button>
                <Box>
                  <IconButton
                    size="small"
                    onClick={() => handleDeleteTextbook(textbook.id)}
                    sx={{ color: 'error.main' }}
                  >
                    <DeleteIcon />
                  </IconButton>
                </Box>
              </Box>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Textbook</DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <TextField
              fullWidth
              label="Title"
              value={newTextbook.title}
              onChange={(e) => setNewTextbook({ ...newTextbook, title: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Author"
              value={newTextbook.author}
              onChange={(e) => setNewTextbook({ ...newTextbook, author: e.target.value })}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              label="Description"
              multiline
              rows={3}
              value={newTextbook.description}
              onChange={(e) => setNewTextbook({ ...newTextbook, description: e.target.value })}
              sx={{ mb: 2 }}
            />
            <Paper
              variant="outlined"
              sx={{
                p: 2,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexDirection: 'column',
                cursor: 'pointer',
                bgcolor: isDarkMode ? 'background.paper' : 'grey.50'
              }}
              onClick={() => document.getElementById('file-upload').click()}
            >
              <input
                id="file-upload"
                type="file"
                accept=".pdf,.epub"
                style={{ display: 'none' }}
                onChange={handleFileSelect}
              />
              <UploadFileIcon sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
              <Typography variant="body1" color="text.secondary">
                {selectedFile ? selectedFile.name : 'Click to upload PDF or EPUB file'}
              </Typography>
            </Paper>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateTextbook}
            disabled={!newTextbook.title || !newTextbook.author || !selectedFile}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TextbookDashboard; 