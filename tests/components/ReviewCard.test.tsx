import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ReviewCard from '../../components/ReviewCard';
import { loadRealTweets } from '../../utils/testDataLoader';

describe('ReviewCard Component', () => {
  // Load real data
  const realTweets = loadRealTweets();
  // Use the first tweet which has rich metadata (people, communities, location)
  // Tweet ID: 1991484499914551567
  const testEvent = realTweets[0];

  if (!testEvent) {
    throw new Error('No real tweets loaded for testing');
  }

  it('renders tweet text', () => {
    render(<ReviewCard event={testEvent} onApprove={() => { }} onEdit={() => { }} />);
    // Check for a substring of the real text
    // Text starts with: "नवा रायपुर में स्थापित जनजातीय संग्रहालय..."
    const textSnippet = "नवा रायपुर में स्थापित";
    expect(screen.getByText((content) => content.includes(textSnippet))).toBeDefined();
  });

  it('displays new metadata fields', () => {
    render(<ReviewCard event={testEvent} onApprove={() => { }} onEdit={() => { }} />);
    
    // The first tweet has "Muriya" community mentioned
    expect(screen.getByText('समुदाय')).toBeDefined();
    const communityElements = screen.getAllByText('मुरिया');
    expect(communityElements.length).toBeGreaterThan(0);

    // Also check for location "Nava Raipur"
    const locationElements = screen.getAllByText((content) => content.includes('नवा रायपुर'));
    expect(locationElements.length).toBeGreaterThan(0);
  });

  it('handles analytics exclusion checkbox', () => {
    const onApprove = vi.fn();
    render(<ReviewCard event={testEvent} onApprove={onApprove} onEdit={() => { }} />);

    const checkbox = screen.getByRole('checkbox');
    expect(checkbox).not.toBeChecked();

    // Check the box
    fireEvent.click(checkbox);
    expect(checkbox).toBeChecked();

    // Click Approve
    fireEvent.click(screen.getByText('स्वीकृत करें'));

    // Verify onApprove was called with true (exclude = true)
    expect(onApprove).toHaveBeenCalledWith(true);
  });

  it('activates edit mode when edit button clicked', () => {
    render(<ReviewCard event={testEvent} onApprove={() => { }} onEdit={() => { }} />);

    // Click the edit button
    fireEvent.click(screen.getByText(/संशोधन करें/));

    // Verify edit mode is activated by checking for save button
    expect(screen.getByText(/सहेजें/)).toBeInTheDocument();
  });

  it('does NOT show Reject button', () => {
    render(<ReviewCard event={testEvent} onApprove={() => { }} onEdit={() => { }} />);
    expect(screen.queryByText('अस्वीकार करें')).toBeNull();
  });
});
