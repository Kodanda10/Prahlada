import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Ingestion from '../../pages/Ingestion';
import React from 'react';

vi.mock('../../services/api', () => ({
  fetchEvents: vi.fn().mockResolvedValue([
    {
      tweet_id: '123',
      clean_text: 'Test Ingest Tweet',
      created_at: '2023-01-01',
      parsing_status: 'SUCCESS',
      event_type: ['Meeting'],
      location_text: 'Raipur'
    }
  ]),
  fetchStats: vi.fn().mockResolvedValue({
    total_tweets: 100,
    pending: 10,
    parsed_success: 90
  })
}));

describe('Ingestion Page', () => {
  it('renders ingestion interface', async () => {
    render(<Ingestion />);
    expect(await screen.findByText(/डेटा अंतर्ग्रहण और पार्सिंग/i)).toBeInTheDocument();
    expect(await screen.findByText(/Test Ingest Tweet/i)).toBeInTheDocument();
  });
});
