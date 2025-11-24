import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Home from '../../pages/Home';
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

vi.mock('../../components/interactions/RiveLikeIcons', () => ({
  PulseButton: () => <button>Refresh</button>,
}));

vi.mock('../../components/TweetPreviewModal', () => ({
  default: () => <div data-testid="modal" />,
}));

vi.mock('../../components/controlhub/ReviewStatusControl', () => ({
  default: () => <div data-testid="review-status-control" />,
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
  it('renders the home page with title', () => {
    render(
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    );
    // Check for the Hindi title
    expect(screen.getByText('ट्वीट डेटाबेस')).toBeInTheDocument();
    // Check for filter inputs
    expect(screen.getByPlaceholderText('स्थान फ़िल्टर...')).toBeInTheDocument();
  });
});
