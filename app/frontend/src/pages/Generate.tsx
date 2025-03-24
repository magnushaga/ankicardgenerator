import { useState } from 'react';
import { 
  Box, 
  TextField, 
  Button, 
  Typography, 
  CircularProgress, 
  Alert,
  Paper
} from '@mui/material';

export default function Generate() {
  const [textbookName, setTextbookName] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await fetch('/api/generate-textbook-structure', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          textbook_name: textbookName,
          test_mode: false
        }),
      });

      const data = await response.json();
      if (response.ok) {
        setResult(data);
      } else {
        setError(data.error || 'Failed to generate deck');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Generate New Deck
        </Typography>

        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            fullWidth
            label="Textbook Name"
            value={textbookName}
            onChange={(e) => setTextbookName(e.target.value)}
            disabled={loading}
            sx={{ mb: 2 }}
          />

          <Button
            variant="contained"
            type="submit"
            disabled={loading || !textbookName}
            startIcon={loading && <CircularProgress size={20} />}
          >
            Generate Deck
          </Button>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {error}
          </Alert>
        )}

        {result && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Generated Structure:
            </Typography>
            <Paper sx={{ p: 2, bgcolor: 'grey.100' }}>
              <pre style={{ overflow: 'auto', maxHeight: '400px' }}>
                {JSON.stringify(result, null, 2)}
              </pre>
            </Paper>
          </Box>
        )}
      </Paper>
    </Box>
  );
} 