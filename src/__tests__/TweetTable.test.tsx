/**
 * TweetTable.test.tsx
 * Tests for Home page कौन/टैग data source and date typography
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import TweetTable from '../components/home/TweetTable';
import { ParsedEvent } from '../src/types';

// Mock parsed event with LLM data
const mockEventWithPeople: ParsedEvent = {
    tweet_id: 'test-1',
    author_handle: 'test_user',
    raw_text: 'Test tweet content',
    created_at: '2025-11-13T10:00:00Z',
    processing_status: 'SUCCESS',
    fetched_at: '2025-11-13T10:00:00Z',
    processed_at: '2025-11-13T10:00:00Z',
    is_parsed: true,
    parsed_event_id: 'parsed-1',
    review_status: 'approved',
    export_timestamp: '2025-11-13T10:00:00Z',
    export_version: '1.0',
    is_clean: true,
    parsed_data_v8: {
        event_type: 'दौरा',
        event_type_secondary: [],
        event_date: '2025-11-13',
        location: { district: 'रायपुर' },
        people_mentioned: ['राम', 'श्याम', 'गीता'],
        people_canonical: ['राम शर्मा', 'श्याम वर्मा'],
        schemes_mentioned: [],
        word_buckets: [],
        target_groups: [],
        communities: [],
        organizations: [],
        hierarchy_path: [],
        visit_count: 1,
        vector_embedding_id: null,
        confidence: 0.9,
        review_status: 'approved',
        needs_review: false,
        content_mode: 'normal',
        is_other_original: false,
        is_rescued_other: false,
        rescue_tag: null,
        rescue_confidence_bonus: 0,
        semantic_location_used: false,
        location_type: 'rural',
    },
    metadata_v8: {
        model: 'gemma-3',
        processing_time_ms: 100,
        version: '8.0',
    },
};

// Mock event without people data
const mockEventWithoutPeople: ParsedEvent = {
    ...mockEventWithPeople,
    tweet_id: 'test-2',
    parsed_data_v8: {
        ...mockEventWithPeople.parsed_data_v8,
        people_mentioned: [],
        people_canonical: [],
    },
};

describe('TweetTable', () => {
    const mockHandlers = {
        onPageChange: vi.fn(),
        onMouseEnter: vi.fn(),
        onMouseLeave: vi.fn(),
    };

    describe('Item 1: कौन/टैग Data Source', () => {
        it('renders people_canonical when available', () => {
            render(
                <TweetTable
                    tweets={[mockEventWithPeople]}
                    currentPage={1}
                    totalPages={1}
                    {...mockHandlers}
                />
            );

            // Should show people_canonical values
            expect(screen.getByText('राम शर्मा')).toBeInTheDocument();
            expect(screen.getByText('श्याम वर्मा')).toBeInTheDocument();
        });

        it('shows empty state when no LLM people data', () => {
            render(
                <TweetTable
                    tweets={[mockEventWithoutPeople]}
                    currentPage={1}
                    totalPages={1}
                    {...mockHandlers}
                />
            );

            // Should show Hindi empty state
            expect(screen.getByText('कोई व्यक्ति नहीं')).toBeInTheDocument();
        });

        it('does NOT use legacy entities.people field', () => {
            const eventWithLegacy = {
                ...mockEventWithoutPeople,
                tweet_id: 'test-3',
                parsed_data_v8: {
                    ...mockEventWithoutPeople.parsed_data_v8,
                    entities: { people: ['Legacy Person'] }, // Legacy field - should be ignored
                },
            };

            render(
                <TweetTable
                    tweets={[eventWithLegacy as any]}
                    currentPage={1}
                    totalPages={1}
                    {...mockHandlers}
                />
            );

            // Should NOT show legacy data
            expect(screen.queryByText('Legacy Person')).not.toBeInTheDocument();
            // Should show empty state instead
            expect(screen.getByText('कोई व्यक्ति नहीं')).toBeInTheDocument();
        });
    });

    describe('Item 2: Date Row Typography', () => {
        it('date cell uses text-sm class for proper sizing', () => {
            render(
                <TweetTable
                    tweets={[mockEventWithPeople]}
                    currentPage={1}
                    totalPages={1}
                    {...mockHandlers}
                />
            );

            // Find the date cell
            const dateCell = screen.getByText(/गुरुवार|शुक्रवार|शनिवार|रविवार|सोमवार|मंगलवार|बुधवार/i)
                .closest('td');

            expect(dateCell).toHaveClass('text-sm');
            expect(dateCell).toHaveClass('leading-relaxed');
        });
    });
});
