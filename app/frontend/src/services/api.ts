const BASE_URL = '/api';

export interface Deck {
  id: string;
  title: string;
  subject?: string;
  cardCount: number;
}

export interface Card {
  id: string;
  front: string;
  back: string;
}

export const api = {
  // Deck operations
  getDecks: async (): Promise<Deck[]> => {
    const res = await fetch(`${BASE_URL}/decks`);
    return res.json();
  },

  getDeck: async (id: string): Promise<Deck> => {
    const res = await fetch(`${BASE_URL}/decks/${id}`);
    return res.json();
  },

  // Search operations
  search: async (query: string, subject?: string) => {
    const res = await fetch(`${BASE_URL}/search?q=${query}${subject ? `&subject=${subject}` : ''}`);
    return res.json();
  },

  // Generation
  generateDeck: async (textbookName: string) => {
    const res = await fetch(`${BASE_URL}/generate-deck`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ textbook_name: textbookName })
    });
    return res.json();
  },

  // Study session
  startStudySession: async (deckId: string) => {
    const res = await fetch(`${BASE_URL}/study/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ deck_id: deckId })
    });
    return res.json();
  },

  getNextCard: async (deckId: string, sessionId: string): Promise<Card | null> => {
    const res = await fetch(`${BASE_URL}/study/next-card?deck_id=${deckId}&session_id=${sessionId}`);
    return res.json();
  },

  submitReview: async (cardId: string, sessionId: string, quality: number) => {
    const res = await fetch(`${BASE_URL}/study/review`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        card_id: cardId,
        session_id: sessionId,
        quality,
        time_taken: Date.now()
      })
    });
    return res.json();
  }
}; 