import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Review from '../../pages/Review';
import React from 'react';

describe('ReviewBreadcrumbs', () => {
  it('shows correct breadcrumb hierarchy', async () => {
    // Mock fetch for Review page
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ([
        {
          tweet_id: '123',
          raw_text: 'Test Review Tweet',
          parsed_data_v8: { location: { district: 'Raipur' } },
          review_status: 'pending'
        }
      ])
    });

    render(<Review />);
    // Wait for main content to load
    expect(await screen.findByText(/समीक्षा कतार/i)).toBeInTheDocument();
    expect(screen.getByText(/AI समीक्षा सहायक/i)).toBeInTheDocument();
  });
});
