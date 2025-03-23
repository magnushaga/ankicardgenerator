import axios from 'axios';
import { DeckGenerationData } from '@/components/features/deck/DeckGenerationForm';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface GeneratedDeck {
  id: string;
  name: string;
  description: string;
  cardCount: number;
  cards: Array<{
    id: string;
    front: string;
    back: string;
  }>;
}

export const deckService = {
  async generateDeck(data: DeckGenerationData): Promise<GeneratedDeck> {
    try {
      const response = await api.post('/generate-textbook-structure', {
        textbook_name: data.textbookName,
      });
      
      // First get the structure and analysis
      const structure = response.data;
      
      // Create a new deck with the generated structure
      const deckResponse = await api.post('/decks', {
        name: `${data.textbookName} Deck`,
        description: `Generated deck for ${data.textbookName}`,
        cardCount: data.cardCount,
        difficultyLevel: data.difficultyLevel,
        focusAreas: data.focusAreas,
        structure: structure,
      });
      
      return deckResponse.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to generate deck');
      }
      throw error;
    }
  },

  async getDeck(id: string): Promise<GeneratedDeck> {
    try {
      const response = await api.get(`/decks/${id}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to fetch deck');
      }
      throw error;
    }
  },

  async getMyDecks(): Promise<GeneratedDeck[]> {
    try {
      const response = await api.get('/decks');
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to fetch decks');
      }
      throw error;
    }
  },

  async searchDecks(query: string): Promise<GeneratedDeck[]> {
    try {
      const response = await api.get('/decks/search', {
        params: { q: query }
      });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.message || 'Failed to search decks');
      }
      throw error;
    }
  }
};