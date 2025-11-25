import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ReviewCard from '../../components/ReviewCard';
import { ParsedEvent, ParsedLocation } from '../../types';

describe('ReviewCard Component', () => {
  // Mock location data
  const mockLocation: ParsedLocation = {
    canonical: 'रायगढ़',
    district: 'रायगढ़',
    location_type: 'district',
    hierarchy_path: ['छत्तीसगढ़', 'रायगढ़'],
    visit_count: 1
  };

  // Mock event data for testing
  const mockEvent: ParsedEvent = {
    tweet_id: '123456789',
    author_handle: 'test_user',
    raw_text: 'आज रायगढ़ में किसानों की बड़ी सभा आयोजित की गई। मुख्यमंत्री ने किसानों को संबोधित किया।',
    created_at: '2024-01-15T10:00:00Z',
    processing_status: 'completed',
    fetched_at: '2024-01-15T09:00:00Z',
    processed_at: '2024-01-15T09:30:00Z',
    is_parsed: true,
    parsed_event_id: 'evt_123',
    review_status: 'pending',
    export_timestamp: '2024-01-15T10:00:00Z',
    export_version: 'v8',
    is_clean: true,
    parsed_data_v8: {
      event_type: 'सभा',
      event_type_secondary: [],
      event_date: '2024-01-15',
      location: mockLocation,
      people_mentioned: ['मुख्यमंत्री'],
      people_canonical: [],
      schemes_mentioned: [],
      word_buckets: [],
      target_groups: ['किसान', 'महिलाएं'],
      communities: [],
      organizations: [],
      hierarchy_path: ['छत्तीसगढ़', 'रायगढ़'],
      visit_count: 1,
      vector_embedding_id: null,
      confidence: 0.95,
      review_status: 'pending',
      needs_review: false,
      content_mode: 'normal',
      is_other_original: false,
      is_rescued_other: false,
      rescue_tag: null,
      rescue_confidence_bonus: 0,
      semantic_location_used: false,
      location_type: 'district'
    },
    metadata_v8: {
      model: 'gemini-pro',
      processing_time_ms: 500,
      version: 'v8'
    }
  };

  it('renders tweet text', () => {
    render(<ReviewCard event={mockEvent} onApprove={() => { }} onEdit={() => { }} />);
    // Check for a substring of the text to avoid issues with long text or formatting
    const textSnippet = mockEvent.raw_text.substring(0, 20);
    expect(screen.getByText((content) => content.includes(textSnippet))).toBeDefined();
  });

  it('displays new metadata fields', () => {
    render(<ReviewCard event={mockEvent} onApprove={() => { }} onEdit={() => { }} />);
    expect(screen.getByText('लक्ष्य समूह')).toBeDefined();
    // Use getAllByText since "किसान" appears multiple times
    const targetElements = screen.getAllByText('किसान');
    expect(targetElements.length).toBeGreaterThan(0);
  });

  it('handles analytics exclusion checkbox', () => {
    const onApprove = vi.fn();
    render(<ReviewCard event={mockEvent} onApprove={onApprove} onEdit={() => { }} />);

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
    render(<ReviewCard event={mockEvent} onApprove={() => { }} onEdit={() => { }} />);

    // Click the edit button
    fireEvent.click(screen.getByText(/संशोधन करें/));

    // Verify edit mode is activated by checking for save button
    expect(screen.getByText(/सहेजें/)).toBeInTheDocument();
  });

  it('does NOT show Reject button', () => {
    render(<ReviewCard event={mockEvent} onApprove={() => { }} onEdit={() => { }} />);
    expect(screen.queryByText('अस्वीकार करें')).toBeNull();
  });
});
