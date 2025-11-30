import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Events from '../../pages/Events';
import React from 'react';

vi.mock('../../services/api', () => ({
  fetchEvents: vi.fn().mockResolvedValue([
    {
      tweet_id: '123',
      clean_text: 'Test Event Tweet',
      created_at: '2023-01-01',
      event_type: ['Meeting'],
      location_text: 'Raipur',
      scheme_tags: ['Scheme A']
    }
  ])
}));

describe('Events Page', () => {
  it('renders events dashboard', async () => {
    render(<Events />);
    expect(await screen.findByText(/इवेंट एक्सप्लोरर/i)).toBeInTheDocument();
    expect(await screen.findByText(/Test Event Tweet/i)).toBeInTheDocument();
  });
});
