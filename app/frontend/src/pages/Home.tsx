import { useEffect, useState } from 'react';
import { Typography, Grid } from '@mui/material';
import { api } from '../services/api';
import DeckCard from '../components/DeckCard';

export default function Home() {
  const [decks, setDecks] = useState([]);

  useEffect(() => {
    const loadDecks = async () => {
      const data = await api.getDecks();
      setDecks(data);
    };
    loadDecks();
  }, []);

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Your Decks
      </Typography>
      <Grid container spacing={3}>
        {decks.map((deck) => (
          <Grid item xs={12} sm={6} md={4} key={deck.id}>
            <DeckCard {...deck} />
          </Grid>
        ))}
      </Grid>
    </>
  );
} 