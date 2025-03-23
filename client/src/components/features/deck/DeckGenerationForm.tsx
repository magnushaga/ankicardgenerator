import { useState } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  CircularProgress,
  Alert,
  Stack,
} from '@mui/material';
import { AutoStories } from '@mui/icons-material';

interface DeckGenerationFormProps {
  onSubmit: (data: DeckGenerationData) => Promise<void>;
}

export interface DeckGenerationData {
  textbookName: string;
  cardCount: number;
  difficultyLevel: 'beginner' | 'intermediate' | 'advanced';
  focusAreas: string[];
}

export default function DeckGenerationForm({ onSubmit }: DeckGenerationFormProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<DeckGenerationData>({
    textbookName: '',
    cardCount: 50,
    difficultyLevel: 'intermediate',
    focusAreas: [],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      await onSubmit(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate deck');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      component="form"
      onSubmit={handleSubmit}
      sx={{
        p: 4,
        maxWidth: 600,
        mx: 'auto',
        bgcolor: 'background.paper',
        borderRadius: 2,
      }}
      elevation={2}
    >
      <Stack spacing={3}>
        <Box sx={{ textAlign: 'center' }}>
          <AutoStories sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
          <Typography variant="h4" component="h1" gutterBottom>
            Generate Deck
          </Typography>
          <Typography color="text.secondary">
            Enter your textbook details and preferences to generate a customized deck
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        <TextField
          fullWidth
          label="Textbook Name"
          value={formData.textbookName}
          onChange={(e) => setFormData({ ...formData, textbookName: e.target.value })}
          required
          variant="outlined"
        />

        <Box>
          <Typography gutterBottom>Number of Cards: {formData.cardCount}</Typography>
          <Slider
            value={formData.cardCount}
            onChange={(_, value) => setFormData({ ...formData, cardCount: value as number })}
            min={10}
            max={200}
            step={10}
            marks={[
              { value: 10, label: '10' },
              { value: 100, label: '100' },
              { value: 200, label: '200' },
            ]}
          />
        </Box>

        <FormControl fullWidth>
          <InputLabel>Difficulty Level</InputLabel>
          <Select
            value={formData.difficultyLevel}
            label="Difficulty Level"
            onChange={(e) => setFormData({
              ...formData,
              difficultyLevel: e.target.value as 'beginner' | 'intermediate' | 'advanced'
            })}
          >
            <MenuItem value="beginner">Beginner</MenuItem>
            <MenuItem value="intermediate">Intermediate</MenuItem>
            <MenuItem value="advanced">Advanced</MenuItem>
          </Select>
        </FormControl>

        <FormControl fullWidth>
          <InputLabel>Focus Areas</InputLabel>
          <Select
            multiple
            value={formData.focusAreas}
            onChange={(e) => setFormData({
              ...formData,
              focusAreas: typeof e.target.value === 'string' ? [e.target.value] : e.target.value,
            })}
            label="Focus Areas"
            renderValue={(selected) => (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip key={value} label={value} />
                ))}
              </Box>
            )}
          >
            <MenuItem value="definitions">Definitions</MenuItem>
            <MenuItem value="concepts">Key Concepts</MenuItem>
            <MenuItem value="examples">Examples</MenuItem>
            <MenuItem value="formulas">Formulas</MenuItem>
            <MenuItem value="applications">Real-world Applications</MenuItem>
          </Select>
        </FormControl>

        <Button
          type="submit"
          variant="contained"
          fullWidth
          size="large"
          disabled={loading || !formData.textbookName}
          sx={{ 
            py: 1.5,
            background: (theme) => 
              `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
          }}
        >
          {loading ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            'Generate Deck'
          )}
        </Button>
      </Stack>
    </Paper>
  );
}