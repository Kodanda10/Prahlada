import { describe, it, expect, vi } from 'vitest';
import { render, waitFor, screen, within } from '@testing-library/react';
import ArbitrationCard from '../../components/ArbitrationCard';
import { ParsedEvent } from '../../types';

// Mock API
vi.mock('../../services/api', () => ({
    default: {
        get: vi.fn().mockResolvedValue({
            tweet_id: 'test-tweet-123',
            raw_text: 'Test Tweet',
            comparison: {}
        }),
        post: vi.fn()
    },
    apiService: {
        get: vi.fn().mockResolvedValue({
            tweet_id: 'test-tweet-123',
            raw_text: 'Test Tweet',
            comparison: {}
        }),
        post: vi.fn()
    }
}));

describe('ArbitrationCard', () => {
    const mockEvent: ParsedEvent = {
        tweet_id: 'test-tweet-123',
        raw_text: 'Test Tweet',
        parsed_data_v8: {
            event_type: 'Meeting',
            event_type_secondary: [],
            event_date: '2023-01-01',
            location: { district: 'Raipur' },
            people_mentioned: [],
            people_canonical: [],
            schemes_mentioned: [],
            word_buckets: [],
            target_groups: [],
            communities: [],
            organizations: [],
            hierarchy_path: [],
            visit_count: 0,
            vector_embedding_id: null,
            confidence: 0.9,
            review_status: 'pending',
            needs_review: true,
            content_mode: 'news',
            is_other_original: false,
            is_rescued_other: false,
            rescue_tag: null,
            rescue_confidence_bonus: 0,
            semantic_location_used: false,
            location_type: 'district'
        },
        metadata_v8: {
            model: 'test',
            processing_time_ms: 100,
            version: '1.0'
        },
        author_handle: 'test_user',
        created_at: new Date().toISOString(),
        processing_status: 'processed',
        fetched_at: new Date().toISOString(),
        processed_at: new Date().toISOString(),
        is_parsed: true,
        parsed_event_id: '123',
        review_status: 'pending',
        export_timestamp: new Date().toISOString(),
        export_version: '1.0',
        is_clean: true
    };

    it('renders without crashing', async () => {
        const { getByText } = render(
            <ArbitrationCard event={mockEvent} onApprove={vi.fn()} />
        );

        // Wait for loading to finish
        await waitFor(() => {
            expect(getByText(/"Test Tweet"/)).toBeInTheDocument();
        });
    });

    it('renders LocationBreadcrumbs', async () => {
        const { getByTestId } = render(
            <ArbitrationCard event={mockEvent} onApprove={vi.fn()} />
        );

        await waitFor(() => {
            const breadcrumbsSection = getByTestId('location-breadcrumbs-section');
            expect(within(breadcrumbsSection).getByText(/Raipur/i)).toBeInTheDocument();
            expect(within(breadcrumbsSection).getByText(/जिला/i)).toBeInTheDocument();
        });
    });

    it('renders Word Bucket section', async () => {
        const eventWithBucket = {
            ...mockEvent,
            parsed_data_v8: {
                ...mockEvent.parsed_data_v8,
                schemes_mentioned: ['Test Scheme'],
                people_canonical: ['Test Person']
            }
        };

        const { getByText } = render(
            <ArbitrationCard event={eventWithBucket} onApprove={vi.fn()} />
        );

        await waitFor(() => {
            expect(getByText('वर्ड बकेट (Word Bucket - Cognitive Input)')).toBeInTheDocument();
            expect(getByText('Test Scheme')).toBeInTheDocument();
            expect(getByText('Test Person')).toBeInTheDocument();
        });
    });
});
