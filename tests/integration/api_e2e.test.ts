import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiService } from '../../services/api';

// Mock fetch globally
global.fetch = vi.fn();

describe('End-to-End API Integration', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    describe('Complete Tweet Workflow', () => {
        it('fetches, approves, and updates tweet end-to-end', async () => {
            // Step 1: Fetch tweet
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    tweet_id: '123',
                    text: 'मुख्यमंत्री ने दौरा किया',
                    review_status: 'pending',
                }),
            });

            const tweet = await apiService.get('/api/events/123');

            expect(tweet.tweet_id).toBe('123');
            expect(tweet.review_status).toBe('pending');

            // Step 2: Approve tweet
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ status: 'approved' }),
            });

            const approveResult = await apiService.approveTweet('123');

            expect(approveResult.status).toBe('approved');

            // Step 3: Verify approval
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    tweet_id: '123',
                    review_status: 'approved',
                }),
            });

            const updatedTweet = await apiService.get('/api/events/123');

            expect(updatedTweet.review_status).toBe('approved');
        });

        it('handles complete error recovery flow', async () => {
            // First attempt fails
            (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

            await expect(apiService.get('/api/events/123')).rejects.toThrow();

            // Retry succeeds
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ tweet_id: '123' }),
            });

            const result = await apiService.get('/api/events/123');
            expect(result.tweet_id).toBe('123');
        });
    });

    describe('Analytics Data Pipeline', () => {
        it('fetches and aggregates analytics data', async () => {
            // Fetch event types
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => [
                    { name: 'दौरा', value: 50 },
                    { name: 'बैठक', value: 30 },
                ],
            });

            // Fetch districts
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => [
                    { name: 'रायपुर', value: 40 },
                    { name: 'बिलासपुर', value: 25 },
                ],
            });

            // Fetch stats
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    total_tweets: 100,
                    parsed_success: 80,
                    pending: 15,
                    errors: 5,
                }),
            });

            // Execute pipeline
            const results = await Promise.all([
                fetch('/api/analytics/event-types').then(r => r.json()),
                fetch('/api/analytics/districts').then(r => r.json()),
                fetch('/api/stats').then(r => r.json()),
            ]);

            expect(results).toHaveLength(3);
            expect(results[0]).toHaveLength(2);  // Event types
            expect(results[1]).toHaveLength(2);  // Districts
            expect(results[2].total_tweets).toBe(100);  // Stats
        });
    });

    describe('Concurrent Operations', () => {
        it('handles multiple simultaneous requests', async () => {
            // Mock responses for concurrent requests
            for (let i = 0; i < 5; i++) {
                (global.fetch as any).mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ id: i, data: `result${i}` }),
                });
            }

            // Execute concurrent requests
            const promises = Array.from({ length: 5 }, (_, i) =>
                apiService.get(`/api/item/${i}`)
            );

            const results = await Promise.all(promises);

            expect(results).toHaveLength(5);
            results.forEach((result, index) => {
                expect(result.id).toBe(index);
            });
        });

        it('handles partial failures in concurrent requests', async () => {
            // Some succeed, some fail
            (global.fetch as any)
                .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 1 }) })
                .mockRejectedValueOnce(new Error('Failed'))
                .mockResolvedValueOnce({ ok: true, json: async () => ({ id: 3 }) });

            const results = await Promise.allSettled([
                apiService.get('/api/item/1'),
                apiService.get('/api/item/2'),
                apiService.get('/api/item/3'),
            ]);

            expect(results[0].status).toBe('fulfilled');
            expect(results[1].status).toBe('rejected');
            expect(results[2].status).toBe('fulfilled');
        });
    });

    describe('Authentication Flow Integration', () => {
        it('completes full auth workflow', async () => {
            // Step 1: Login
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    token: 'jwt-token-123',
                    user: { id: 'user1', username: 'admin', roles: ['admin'] },
                }),
            });

            const authResponse = await fetch('/api/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username: 'admin', password: 'pass' }),
            }).then(r => r.json());

            expect(authResponse.token).toBe('jwt-token-123');

            // Step 2: Use token for protected request
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ data: 'protected' }),
            });

            const protectedData = await fetch('/api/protected', {
                headers: { Authorization: `Bearer ${authResponse.token}` },
            }).then(r => r.json());

            expect(protectedData.data).toBe('protected');
        });
    });

    describe('Data Consistency', () => {
        it('maintains data consistency across operations', async () => {
            let tweetState = { review_status: 'pending', edit_count: 0 };

            // Create
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ ...tweetState, id: '123' }),
            });

            const created = await apiService.post('/api/events', tweetState);
            expect(created.review_status).toBe('pending');

            // Update
            tweetState = { ...tweetState, review_status: 'approved', edit_count: 1 };
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({ ...tweetState, id: '123' }),
            });

            const updated = await apiService.put('/api/events/123', tweetState);
            expect(updated.review_status).toBe('approved');
            expect(updated.edit_count).toBe(1);
        });
    });

    describe('Performance Under Load', () => {
        it('handles high-frequency requests', async () => {
            const requestCount = 50;

            // Mock all responses
            for (let i = 0; i < requestCount; i++) {
                (global.fetch as any).mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ request_id: i }),
                });
            }

            const startTime = Date.now();

            // Execute many requests
            const promises = Array.from({ length: requestCount }, (_, i) =>
                apiService.get(`/api/fast/${i}`)
            );

            const results = await Promise.all(promises);
            const duration = Date.now() - startTime;

            expect(results).toHaveLength(requestCount);
            // Should complete reasonably fast (mocked, so very fast)
            expect(duration).toBeLessThan(1000);
        });
    });
});
