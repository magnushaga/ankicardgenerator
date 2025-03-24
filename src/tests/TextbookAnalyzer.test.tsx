import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import TextbookAnalyzer from '../components/TextbookAnalyzer';

// Mock fetch globally
global.fetch = jest.fn();

describe('TextbookAnalyzer Component', () => {
  beforeEach(() => {
    (global.fetch as jest.Mock).mockClear();
  });

  it('renders the input field and button', () => {
    render(<TextbookAnalyzer />);
    
    expect(screen.getByPlaceholderText('Enter textbook name')).toBeInTheDocument();
    expect(screen.getByText('Analyze Textbook')).toBeInTheDocument();
  });

  it('handles textbook analysis in test mode', async () => {
    const mockResponse = {
      primary_subject: 'Computer Science',
      subfields: ['Programming'],
      requires_math: false
    };

    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockResponse)
      })
    );

    render(<TextbookAnalyzer />);

    // Enter textbook name
    const input = screen.getByPlaceholderText('Enter textbook name');
    fireEvent.change(input, { target: { value: 'Test Book' } });

    // Click analyze button
    const button = screen.getByText('Analyze Textbook');
    fireEvent.click(button);

    // Wait for results
    await waitFor(() => {
      expect(screen.getByText(/Computer Science/)).toBeInTheDocument();
    });
  });
}); 