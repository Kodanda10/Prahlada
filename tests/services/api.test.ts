import { describe, it, expect, vi, beforeEach } from 'vitest';
import {
    fetchStats,
    fetchEvents,
    fetchAnalyticsData,
    apiService,
    setApiAuthToken,
    AuthAPI,
} from '../../services/api';

// Mock fetch
global.fetch = vi.fn();

describe('API Service Tests', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        setApiAuthToken(null);
    });

    describe('fetchStats', () => {
        it('fetches stats successfully', async () => {
            const mockStats = {
                total_tweets: 100,
                parsed_success: 80,
                pending: 15,
                errors: 5,
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockStats,
            });

            const stats = await fetchStats();

            expect(stats).toEqual(mockStats);
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/stats'),
                expect.any(Object)
            );
        });

        it('returns zero stats on error', async () => {
            (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

            const stats = await fetchStats();

            expect(stats.total_tweets).toBe(0);
            expect(stats.parsed_success).toBe(0);
        });
    });

    describe('fetchEvents', () => {
        it('fetches all events by default', async () => {
            const mockEvents = [
                { tweet_id: '1', text: 'Event 1' },
                { tweet_id: '2', text: 'Event 2' },
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockEvents,
            });

            const events = await fetchEvents();

            expect(events).toHaveLength(2);
            expect(events[0].tweet_id).toBe('1');
        });

        it('filters failed events', async () => {
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => [],
            });

            await fetchEvents('failed');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('status=FAILED'),
                expect.any(Object)
            );
        });

        it('returns empty array on error', async () => {
            (global.fetch as any).mockRejectedValueOnce(new Error('Fetch failed'));

            const events = await fetchEvents();

            expect(events).toEqual([]);
        });
    });

    describe('fetchAnalyticsData', () => {
        it('fetches event types analytics', async () => {
            const mockData = [
                { name: 'दौरा', value: 50 },
                { name: 'बैठक', value: 30 },
            ];

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockData,
            });

            const data = await fetchAnalyticsData('event-types');

            expect(data).toEqual(mockData);
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/analytics/event-types'),
                expect.any(Object)
            );
        });

        it('fetches districts analytics', async () => {
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => [],
            });

            await fetchAnalyticsData('districts');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/analytics/districts'),
                expect.any(Object)
            );
        });
    });

    describe('apiService', () => {
        describe('GET requests', () => {
            it('performs GET request correctly', async () => {
                const mockData = { success: true };

                (global.fetch as any).mockResolvedValueOnce({
                    ok: true,
                    json: async () => mockData,
                });

                const result = await apiService.get('/test-endpoint');

                expect(result).toEqual(mockData);
            });

            it('throws error on failed GET', async () => {
                (global.fetch as any).mockResolvedValueOnce({
                    ok: false,
                    status: 404,
                    statusText: 'Not Found',
                });

                await expect(apiService.get('/not-found')).rejects.toThrow();
            });
        });

        describe('POST requests', () => {
            it('performs POST request with data', async () => {
                const requestData = { name: 'test' };
                const responseData = { id: 1, name: 'test' };

                (global.fetch as any).mockResolvedValueOnce({
                    ok: true,
                    json: async () => responseData,
                });

                const result = await apiService.post('/create', requestData);

                expect(result).toEqual(responseData);
                expect(global.fetch).toHaveBeenCalledWith(
                    expect.any(String),
                    expect.objectContaining({
                        method: 'POST',
                        body: JSON.stringify(requestData),
                    })
                );
            });
        });

        describe('PUT requests', () => {
            it('performs PUT request correctly', async () => {
                const updateData = { status: 'updated' };

                (global.fetch as any).mockResolvedValueOnce({
                    ok: true,
                    json: async () => updateData,
                });

                const result = await apiService.put('/update/1', updateData);

                expect(result).toEqual(updateData);
            });
        });

        describe('DELETE requests', () => {
            it('performs DELETE request correctly', async () => {
                (global.fetch as any).mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true }),
                });

                const result = await apiService.delete('/item/1');

                expect(result).toEqual({ success: true });
            });
        });

        describe('approveTweet', () => {
            it('approves tweet by ID', async () => {
                (global.fetch as any).mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ status: 'approved' }),
                });

                const result = await apiService.approveTweet('tweet123');

                expect(result).toEqual({ status: 'approved' });
                expect(global.fetch).toHaveBeenCalledWith(
                    expect.stringContaining('/api/events/tweet123/approve'),
                    expect.objectContaining({ method: 'POST' })
                );
            });
        });
    });

    describe('Authentication', () => {
        it('sets auth token correctly', () => {
            setApiAuthToken('test-token-123');

            // Token should be included in subsequent requests
            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({}),
            });

            apiService.get('/protected');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    headers: expect.objectContaining({
                        Authorization: 'Bearer test-token-123',
                    }),
                })
            );
        });

        it('makes requests without token when not set', () => {
            setApiAuthToken(null);

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => ({}),
            });

            apiService.get('/public');

            expect(global.fetch).toHaveBeenCalledWith(
                expect.any(String),
                expect.objectContaining({
                    headers: expect.not.objectContaining({
                        Authorization: expect.any(String),
                    }),
                })
            );
        });
    });

    describe('AuthAPI', () => {
        it('logs in successfully', async () => {
            const mockAuthResponse = {
                token: 'jwt-token-here',
                user: {
                    id: 'user123',
                    username: 'admin',
                    roles: ['admin'],
                    displayName: 'Admin User',
                },
            };

            (global.fetch as any).mockResolvedValueOnce({
                ok: true,
                json: async () => mockAuthResponse,
            });

            const result = await AuthAPI.login('admin', 'password');

            expect(result.token).toBe('jwt-token-here');
            expect(result.user.username).toBe('admin');
            expect(result.user.roles).toContain('admin');
        });

        it('throws error on failed login', async () => {
            (global.fetch as any).mockResolvedValueOnce({
                ok: false,
                status: 401,
                statusText: 'Unauthorized',
            });

            await expect(AuthAPI.login('wrong', 'credentials')).rejects.toThrow();
        });
    });
});
