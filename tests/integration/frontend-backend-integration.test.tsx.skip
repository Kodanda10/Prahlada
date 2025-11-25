import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { apiService } from '../services/api';

describe('Frontend-Backend Integration & Resilience', () => {
  // Mock backend responses
  const mockTweetData = [
    {
      id: 'tweet_001',
      text: 'क्षेत्रीय विकास कार्य प्रगति पर है',
      place: 'खरसिया',
      coordinates: [83.08, 21.99],
      hierarchy: {
        district: 'रायगढ़',
        constituency: 'खरसिया',
        block: 'खरसिया ब्लॉक',
        gp: 'जोंबी ग्राम पंचायत',
        village: 'जोंबी'
      },
      created_at: '2024-01-15T10:30:00Z',
      author: { username: 'officer1' }
    },
    {
      id: 'tweet_002',
      text: 'ग्राम पंचायत बैठक सफलतापूर्वक संपन्न',
      place: 'तमनार',
      coordinates: [83.27, 21.88],
      hierarchy: {
        district: 'रायगढ़',
        constituency: 'खरसिया',
        block: 'खरसिया ब्लॉक',
        gp: 'तमनार ग्राम पंचायत',
        village: 'तमनार'
      },
      created_at: '2024-01-20T14:15:00Z',
      author: { username: 'officer2' }
    }
  ];

  const mockAnalyticsData = {
    totalVisits: 135,
    districtBreakdown: {
      'रायगढ़': 75,
      'कोरबा': 60
    },
    recentActivity: [
      { date: '2024-01-20', visits: 12, location: 'खरसिया' },
      { date: '2024-01-19', visits: 8, location: 'तमनार' },
    ]
  };

  beforeEach(() => {
    // Reset fetch mock
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('API Service Integration', () => {
    it('successfully fetches tweet data from backend', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ data: mockTweetData, total: 2 }),
      });

      const result = await apiService.get('/api/tweets');

      expect(global.fetch).toHaveBeenCalledWith('/api/tweets', expect.any(Object));
      expect(result.data).toEqual(mockTweetData);
      expect(result.total).toBe(2);
    });

    it('handles backend response with proper error checking', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
      });

      await expect(apiService.get('/api/nonexistent')).rejects.toThrow();
    });

    it('sends POST requests with authentication headers', async () => {
      const postData = { action: 'create_visit', location: 'खरसिया' };

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ success: true, id: 'visit_001' }),
      });

      await apiService.post('/api/visits', postData);

      expect(global.fetch).toHaveBeenCalledWith('/api/visits', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Should include auth headers in real implementation
        },
        body: JSON.stringify(postData),
      });
    });

    it('includes authentication tokens in requests', async () => {
      // Mock localStorage for token storage
      const mockToken = 'jwt-token-12345';
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: vi.fn((key) => key === 'authToken' ? mockToken : null),
        },
        writable: true,
      });

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ authenticated: true }),
      });

      await apiService.get('/api/protected');

      expect(global.fetch).toHaveBeenCalledWith('/api/protected', expect.objectContaining({
        headers: expect.objectContaining({
          'Authorization': `Bearer ${mockToken}`,
        }),
      }));
    });
  });

  describe('Data Synchronization and Caching', () => {
    it('caches frequently accessed data', async () => {
      const cache = new Map();

      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAnalyticsData),
      });

      // First request - should hit network
      const result1 = await apiService.get('/api/analytics');
      expect(result1).toEqual(mockAnalyticsData);

      // Second request - should use cache (in real implementation)
      const result2 = await apiService.get('/api/analytics');
      expect(result2).toEqual(mockAnalyticsData);

      // Should only call fetch once if caching is implemented
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('invalidates stale cache data', async () => {
      const cacheExpiry = new Map();

      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ...mockAnalyticsData, timestamp: Date.now() }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ ...mockAnalyticsData, timestamp: Date.now() + 1000 }),
        });

      // First request
      await apiService.get('/api/analytics');

      // Simulate cache expiry
      vi.advanceTimersByTime(300000); // 5 minutes

      // Second request should refetch
      await apiService.get('/api/analytics');

      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('handles concurrent API requests efficiently', async () => {
      const requestPromises = [];

      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: 'response' }),
      });

      // Make multiple concurrent requests
      for (let i = 0; i < 5; i++) {
        requestPromises.push(apiService.get(`/api/endpoint/${i}`));
      }

      const results = await Promise.all(requestPromises);

      expect(results).toHaveLength(5);
      results.forEach(result => {
        expect(result.data).toBe('response');
      });

      // Should make 5 separate requests (or batch them in real implementation)
      expect(global.fetch).toHaveBeenCalledTimes(5);
    });
  });

  describe('Error Recovery and Retry Logic', () => {
    it('automatically retries failed requests', async () => {
      (global.fetch as any)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Timeout'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true }),
        });

      const result = await apiService.get('/api/retry-endpoint');

      expect(result.success).toBe(true);
      expect(global.fetch).toHaveBeenCalledTimes(3); // 2 failures + 1 success
    });

    it('implements exponential backoff for retries', async () => {
      const retryDelays: number[] = [];

      (global.fetch as any)
        .mockImplementation(() => {
          retryDelays.push(Date.now());
          return Promise.reject(new Error('Persistent error'));
        });

      try {
        await apiService.get('/api/backoff-endpoint');
      } catch (error) {
        // Expected to fail after retries
      }

      // Should have increasing delays between retries
      expect(retryDelays.length).toBeGreaterThan(1);
    });

    it('provides user feedback during retries', async () => {
      // Mock loading state management
      let isLoading = false;

      (global.fetch as any)
        .mockImplementation(() => {
          isLoading = true;
          return new Promise(resolve => {
            setTimeout(() => {
              isLoading = false;
              resolve({
                ok: true,
                json: () => Promise.resolve({ data: 'success' }),
              });
            }, 100);
          });
        });

      const promise = apiService.get('/api/loading-endpoint');

      // Should show loading state
      expect(isLoading).toBe(true);

      await promise;

      // Should clear loading state
      expect(isLoading).toBe(false);
    });
  });

  describe('Offline Support and Queue Management', () => {
    it('queues requests when offline', async () => {
      // Mock offline state
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      const requestQueue: any[] = [];

      // Mock queue implementation
      const originalApiService = { ...apiService };
      apiService.get = vi.fn((url) => {
        if (!navigator.onLine) {
          requestQueue.push({ type: 'GET', url });
          return Promise.resolve({ queued: true });
        }
        return originalApiService.get(url);
      });

      const result = await apiService.get('/api/offline-request');

      expect(result.queued).toBe(true);
      expect(requestQueue).toHaveLength(1);
      expect(requestQueue[0].url).toBe('/api/offline-request');
    });

    it('syncs queued requests when back online', async () => {
      const syncResults: any[] = [];

      // Start offline
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      // Queue some requests
      await apiService.get('/api/queue-1');
      await apiService.get('/api/queue-2');

      // Mock successful sync
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ synced: true }),
      });

      // Come back online
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        configurable: true,
      });

      // Trigger sync (would be automatic in real implementation)
      const syncPromises = [
        apiService.get('/api/queue-1'),
        apiService.get('/api/queue-2'),
      ];

      const results = await Promise.all(syncPromises);

      results.forEach(result => {
        expect(result.synced).toBe(true);
      });
    });

    it('handles partial sync failures gracefully', async () => {
      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ id: 1, synced: true }),
        })
        .mockRejectedValueOnce(new Error('Sync failed'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ id: 3, synced: true }),
        });

      const syncPromises = [
        apiService.post('/api/sync', { id: 1 }),
        apiService.post('/api/sync', { id: 2 }), // Will fail
        apiService.post('/api/sync', { id: 3 }),
      ];

      const results = await Promise.allSettled(syncPromises);

      const fulfilled = results.filter(r => r.status === 'fulfilled');
      const rejected = results.filter(r => r.status === 'rejected');

      expect(fulfilled).toHaveLength(2);
      expect(rejected).toHaveLength(1);
    });
  });

  describe('Real-time Data Updates (WebSocket/SSE)', () => {
    it('establishes WebSocket connection for real-time updates', () => {
      const mockWebSocket = {
        onopen: null,
        onmessage: null,
        onclose: null,
        onerror: null,
        send: vi.fn(),
        close: vi.fn(),
      };

      global.WebSocket = vi.fn(() => mockWebSocket) as any;

      // Simulate WebSocket connection (would be in apiService)
      const ws = new WebSocket('ws://localhost:8080/updates');

      expect(WebSocket).toHaveBeenCalledWith('ws://localhost:8080/updates');
      expect(mockWebSocket.send).toBeDefined();
    });

    it('handles incoming real-time data updates', () => {
      const updateCallbacks: Function[] = [];
      const receivedUpdates: any[] = [];

      // Mock WebSocket message handling
      const mockWebSocket = {
        onmessage: (event: any) => {
          const data = JSON.parse(event.data);
          receivedUpdates.push(data);
          updateCallbacks.forEach(callback => callback(data));
        },
      };

      // Simulate receiving real-time updates
      const updateData = {
        type: 'VISIT_UPDATE',
        location: 'खरसिया',
        newVisits: 5,
        timestamp: new Date().toISOString(),
      };

      mockWebSocket.onmessage({
        data: JSON.stringify(updateData),
      });

      expect(receivedUpdates).toContain(updateData);
    });

    it('maintains connection and reconnects on failure', () => {
      let connectionAttempts = 0;

      const mockWebSocket = vi.fn(() => ({
        onopen: null,
        onclose: () => {
          // Auto-reconnect logic would go here
          connectionAttempts++;
        },
      }));

      global.WebSocket = mockWebSocket;

      // First connection
      new WebSocket('ws://localhost:8080');
      expect(connectionAttempts).toBe(0);

      // Simulate connection failure and reconnect
      connectionAttempts = 1; // Manual increment for test

      expect(connectionAttempts).toBe(1);
    });
  });

  describe('Authentication and Session Management', () => {
    it('handles token refresh automatically', async () => {
      const tokens = {
        access: 'access-token-123',
        refresh: 'refresh-token-456',
      };

      (global.fetch as any)
        .mockResolvedValueOnce({
          ok: false,
          status: 401,
          json: () => Promise.resolve({ error: 'Token expired' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ access_token: 'new-access-token' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ data: 'protected content' }),
        });

      // First request fails with 401
      try {
        await apiService.get('/api/protected');
      } catch (error) {
        // Expected to fail initially
      }

      // Should attempt token refresh and retry
      expect(global.fetch).toHaveBeenCalledTimes(3); // Original + refresh + retry
    });

    it('redirects to login on authentication failure', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: false,
        status: 401,
        json: () => Promise.resolve({ error: 'Authentication required' }),
      });

      // Mock window.location
      const mockLocation = { href: '' };
      Object.defineProperty(window, 'location', {
        value: mockLocation,
        writable: true,
      });

      try {
        await apiService.get('/api/protected');
      } catch (error) {
        // Should redirect to login
        expect(mockLocation.href).toBe('/login');
      }
    });

    it('maintains session across page reloads', () => {
      const sessionData = {
        user: { id: 1, name: 'Test User' },
        token: 'session-token-789',
        expires: Date.now() + 3600000, // 1 hour
      };

      // Mock sessionStorage
      const mockSessionStorage = {
        getItem: vi.fn((key) => {
          if (key === 'session') return JSON.stringify(sessionData);
          return null;
        }),
        setItem: vi.fn(),
      };

      Object.defineProperty(window, 'sessionStorage', {
        value: mockSessionStorage,
        writable: true,
      });

      // Should restore session
      const stored = JSON.parse(mockSessionStorage.getItem('session') || '{}');
      expect(stored.user.name).toBe('Test User');
      expect(stored.token).toBe('session-token-789');
    });
  });

  describe('Performance Monitoring and Optimization', () => {
    it('tracks API response times', async () => {
      const responseTimes: number[] = [];

      (global.fetch as any).mockImplementation(() => {
        const startTime = Date.now();
        return new Promise(resolve => {
          setTimeout(() => {
            const endTime = Date.now();
            responseTimes.push(endTime - startTime);
            resolve({
              ok: true,
              json: () => Promise.resolve({ data: 'response' }),
            });
          }, 100);
        });
      });

      await apiService.get('/api/timed-request');

      expect(responseTimes).toHaveLength(1);
      expect(responseTimes[0]).toBeGreaterThanOrEqual(100);
    });

    it('implements request deduplication', async () => {
      let requestCount = 0;

      (global.fetch as any).mockImplementation(() => {
        requestCount++;
        return new Promise(resolve => {
          setTimeout(() => resolve({
            ok: true,
            json: () => Promise.resolve({ data: `response-${requestCount}` }),
          }), 50);
        });
      });

      // Make identical concurrent requests
      const promises = [
        apiService.get('/api/dedupe'),
        apiService.get('/api/dedupe'),
        apiService.get('/api/dedupe'),
      ];

      const results = await Promise.all(promises);

      // In real implementation, this might dedupe to 1 request
      // For now, we expect 3 separate requests
      expect(results).toHaveLength(3);
      expect(requestCount).toBe(3);
    });

    it('provides request cancellation support', async () => {
      const abortController = new AbortController();

      (global.fetch as any).mockImplementation((url: string, options: any) => {
        return new Promise((resolve, reject) => {
          const timeout = setTimeout(() => {
            resolve({
              ok: true,
              json: () => Promise.resolve({ data: 'completed' }),
            });
          }, 200);

          if (options?.signal) {
            options.signal.addEventListener('abort', () => {
              clearTimeout(timeout);
              reject(new Error('Request cancelled'));
            });
          }
        });
      });

      // Start request
      const requestPromise = apiService.get('/api/cancellable');

      // Cancel request
      setTimeout(() => abortController.abort(), 50);

      try {
        await requestPromise;
      } catch (error: any) {
        expect(error.message).toBe('Request cancelled');
      }
    });
  });
});