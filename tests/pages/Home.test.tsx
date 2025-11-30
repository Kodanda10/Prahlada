import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '../test-utils';
import Home from '../../pages/Home';
import { MemoryRouter } from 'react-router-dom';
import { ConfigProvider } from '../../contexts/ConfigContext';
import { BrowserRouter } from 'react-router-dom';
import React from 'react';

// Mock the dependencies
vi.mock('lucide-react', () => ({
  Filter: () => <div data-testid="filter-icon" />,
  CheckSquare: () => <div data-testid="check-icon" />,
  MapPin: () => <div data-testid="map-icon" />,
  Tag: () => <div data-testid="tag-icon" />,
  Calendar: () => <div data-testid="calendar-icon" />,
  ExternalLink: () => <div data-testid="link-icon" />,
  Download: () => <div data-testid="download-icon" />,
  X: () => <div data-testid="x-icon" />,
  ChevronLeft: () => <div data-testid="left-icon" />,
  ChevronRight: () => <div data-testid="right-icon" />,
}));

vi.mock('../../components/AnimatedGlassCard', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock services/api
vi.mock('../../services/api', () => ({
  fetchEvents: vi.fn(),
  apiService: {
    get: vi.fn(),
  }
}));

// Mock other components
vi.mock('../../components/interactions/RiveLikeIcons', () => ({
  PulseButton: ({ onClick, isLoading }: any) => (
    <button onClick={onClick}>{isLoading ? 'Loading...' : 'Refresh'}</button>
  ),
}));

vi.mock('../../components/TweetPreviewModal', () => ({
  default: () => <div data-testid="modal" />,
}));

vi.mock('../../components/controlhub/ReviewStatusControl', () => ({
  default: () => <div data-testid="review-status-control" />,
}));

vi.mock('../../components/SectionWrapper', () => ({
  default: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('../../components/home/TweetFilters', () => ({
  default: () => <div data-testid="tweet-filters" />,
}));

vi.mock('../../components/home/TweetTable', () => ({
  default: ({ tweets }: any) => (
    <div data-testid="tweet-table">
      {tweets?.map((t: any) => (
        <div key={t.tweet_id}>
          <span>{t.raw_text}</span>
          <span>{t.parsed_data_v8?.location?.district}</span>
        </div>
      ))}
    </div>
  ),
}));

vi.mock('../../utils/reviewStatusStore', () => ({
  useReviewStatus: () => ({
    showApproved: true,
    showPending: true,
    showSkipped: true,
    toggleApproved: vi.fn(),
    togglePending: vi.fn(),
    toggleSkipped: vi.fn(),
  }),
}));

describe('Home Page', () => {
  it('renders the home page with title', async () => {
    const { fetchEvents } = await import('../../services/api');
    (fetchEvents as any).mockResolvedValue([]);

    render(<Home />);

    // Check if the main title is present
    expect(await screen.findByText('ट्वीट डेटाबेस')).toBeInTheDocument();

    // Check for key UI components
    expect(screen.getByTestId('modal')).toBeInTheDocument();
    expect(screen.getByTestId('tweet-table')).toBeInTheDocument();
  });

  it('renders the Home page with tweets', async () => {
    // Mock API response
    const mockTweets = [
      {
        tweet_id: '1',
        raw_text: 'Test Tweet 1',
        created_at: '2023-10-27T10:00:00Z',
        approved_by_human: false,
        parsed_data_v8: {
          location: { district: 'Raipur' },
          event_type: 'Meeting',
          people_canonical: ['Raman Singh']
        }
      }
    ];

    const { fetchEvents } = await import('../../services/api');
    (fetchEvents as any).mockResolvedValue(mockTweets);

    render(<Home />);

    // Wait for data to load
    expect(await screen.findByText('Test Tweet 1')).toBeInTheDocument();
    expect(screen.getByText('Raipur')).toBeInTheDocument();
  });
});
