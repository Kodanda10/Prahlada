import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '../test-utils';
import Review from '../../pages/Review';

// Mock the fetch API
global.fetch = vi.fn();

describe('Review Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the review page with event cards', async () => {
    const mockEvents = [
      {
        id: 1,
        tweet_id: '12345',
        raw_text: 'Test Tweet',
        parsed_data_v8: {
          event_type: 'राजनीतिक सभा',
          location: { ulb: 'Raipur', type: 'city', lat: 21.25, lng: 81.63 },
          people: ['Raman Singh'],
          people_canonical: ['Raman Singh'],
          schemes: [],
          organizations: [],
          overall_confidence: 0.95,
        },
        review_status: 'pending',
        parsed_at: '2024-01-01T10:00:00Z'
      }
    ];

    (global.fetch as any).mockResolvedValue({
      ok: true,
      json: async () => mockEvents,
    });

    render(<Review />);

    // Wait for loading to finish and heading to appear
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /समीक्षा कतार/i })).toBeInTheDocument();
    });

    // Check for the event type
    expect(screen.getAllByText(/राजनीतिक सभा/i)[0]).toBeInTheDocument();

    // Check for specific event details
    expect(screen.getAllByText(/Raipur/i)[0]).toBeInTheDocument();
    // People are rendered in the Word Bucket, check for presence
    expect(screen.getAllByText(/Raman Singh/i)[0]).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as any).mockRejectedValue(new Error('API Error'));

    render(<Review />);

    await waitFor(() => {
      // Ensure the page still renders the title even if data fetch fails
      expect(screen.getByRole('heading', { name: /समीक्षा कतार/i })).toBeInTheDocument();
    });
  });
});
