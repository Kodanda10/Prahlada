import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ReviewCard from '../../components/ReviewCard';
import realData from '../../data/ingested_tweets.json';
import { ParsedEvent } from '../../types';

describe('ReviewCard Component', () => {
  // Use real data
  const sampleEvent = realData[0] as unknown as ParsedEvent;

  it('renders tweet text', () => {
    render(<ReviewCard event={sampleEvent} onApprove={() => {}} onEdit={() => {}} />);
    // Check for a substring of the text to avoid issues with long text or formatting
    const textSnippet = sampleEvent.raw_text.substring(0, 20);
    expect(screen.getByText((content) => content.includes(textSnippet))).toBeDefined();
  });

  it('displays new metadata fields', () => {
    // Find a tweet with target groups
    const eventWithTargets = realData.find(t => t.parsed_data_v8.target_groups?.length > 0) as unknown as ParsedEvent;
    if (eventWithTargets) {
      render(<ReviewCard event={eventWithTargets} onApprove={() => {}} onEdit={() => {}} />);
      expect(screen.getByText('लक्ष्य समूह')).toBeDefined();
      expect(screen.getByText(eventWithTargets.parsed_data_v8.target_groups[0])).toBeDefined();
    }
  });

  it('handles analytics exclusion checkbox', () => {
    const onApprove = vi.fn();
    render(<ReviewCard event={sampleEvent} onApprove={onApprove} onEdit={() => {}} />);

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

  it('calls onEdit when edit button clicked', () => {
    const onEdit = vi.fn();
    render(<ReviewCard event={sampleEvent} onApprove={() => {}} onEdit={onEdit} />);

    fireEvent.click(screen.getByText('संशोधन करें'));
    expect(onEdit).toHaveBeenCalled();
  });

  it('does NOT show Reject button', () => {
    render(<ReviewCard event={sampleEvent} onApprove={() => {}} onEdit={() => {}} />);
    expect(screen.queryByText('अस्वीकार करें')).toBeNull();
  });
});
