export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  bio?: string;
  createdAt: string;
  lastLogin?: string;
}

export interface Deck {
  id: string;
  userId: string;
  textbookId?: string;
  name: string;
  description?: string;
  cardCount: number;
  createdAt: string;
  updatedAt: string;
  isPublic: boolean;
  tags: string[];
}

export interface Card {
  id: string;
  deckId: string;
  front: string;
  back: string;
  nextReview?: string;
  interval?: number;
  easiness?: number;
  repetitions?: number;
  createdAt: string;
  updatedAt: string;
}

export interface StudySession {
  id: string;
  userId: string;
  deckId: string;
  startedAt: string;
  endedAt?: string;
  cardsStudied: number;
  correctAnswers: number;
}

export interface TextbookAnalysis {
  primarySubject: string;
  subfields: string[];
  requiresMath: boolean;
  requiresChemistryNotation: boolean;
  requiresBiologyNotation: boolean;
  benefitsFromCode: boolean;
  benefitsFromHistory: boolean;
  benefitsFromConcepts: boolean;
  benefitsFromTheory: boolean;
  benefitsFromExamples: boolean;
  benefitsFromQuotes: boolean;
  recommendedFocusAreas: string[];
  specialNotationNeeds: string[];
}

export interface DeckGenerationOptions {
  textbookName: string;
  cardCount?: number;
  includeImages?: boolean;
  difficultyLevel?: 'beginner' | 'intermediate' | 'advanced';
  focusAreas?: string[];
  language?: string;
}

export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, any>;
}