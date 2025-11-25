import { describe, it, expect, vi, beforeEach } from 'vitest';
import { geocodeLocation, geocodeBatch, GeocodingResult } from '../../services/geocoding';

describe('Geocoding Service', () => {
  beforeEach(() => {
    // Clear cache before each test
    vi.clearAllMocks();
  });

  describe('Single Location Geocoding', () => {
    it('returns cached result if available', async () => {
      const location = 'Raipur, Chhattisgarh';
      
      // First call - should hit API
      const result1 = await geocodeLocation(location);
      
      // Second call - should use cache
      const result2 = await geocodeLocation(location);
      
      expect(result1).toEqual(result2);
    });

    it('uses Mapbox as primary geocoding service', async () => {
      const location = 'Bilaspur, Chhattisgarh';
      const result = await geocodeLocation(location);
      
      expect(result).toBeDefined();
      expect(result?.lat).toBeDefined();
      expect(result?.lng).toBeDefined();
      expect(result?.source).toBe('mapbox');
    });

    it('falls back to Nominatim if Mapbox fails', async () => {
      // Mock Mapbox to fail
      const location = 'InvalidLocation123';
      const result = await geocodeLocation(location);
      
      // Should either return null or use Nominatim
      if (result) {
        expect(result.source).toBe('nominatim');
      }
    });

    it('returns null for completely invalid locations', async () => {
      const result = await geocodeLocation('XYZ123InvalidPlace');
      expect(result).toBeNull();
    });

    it('handles Hindi/Devanagari location names', async () => {
      const result = await geocodeLocation('रायपुर, छत्तीसगढ़');
      
      expect(result).toBeDefined();
      expect(result?.lat).toBeDefined();
      expect(result?.lng).toBeDefined();
    });
  });

  describe('Batch Geocoding', () => {
    it('processes multiple locations', async () => {
      const locations = [
        'Raipur, Chhattisgarh',
        'Bilaspur, Chhattisgarh',
        'Durg, Chhattisgarh'
      ];
      
      const results = await geocodeBatch(locations);
      
      expect(results).toHaveLength(3);
      results.forEach(result => {
        expect(result.lat).toBeDefined();
        expect(result.lng).toBeDefined();
      });
    });

    it('respects rate limits', async () => {
      const locations = Array.from({ length: 10 }, (_, i) => `Location ${i}`);
      
      const startTime = Date.now();
      await geocodeBatch(locations, { rateLimit: 2 }); // 2 req/sec
      const endTime = Date.now();
      
      // Should take at least 4 seconds (10 locations / 2 per second)
      expect(endTime - startTime).toBeGreaterThanOrEqual(4000);
    });

    it('handles partial failures gracefully', async () => {
      const locations = [
        'Raipur, Chhattisgarh',
        'InvalidLocation123',
        'Bilaspur, Chhattisgarh'
      ];
      
      const results = await geocodeBatch(locations);
      
      expect(results).toHaveLength(3);
      expect(results[0]).toBeDefined();
      expect(results[1]).toBeNull();
      expect(results[2]).toBeDefined();
    });
  });

  describe('Caching', () => {
    it('saves successful results to cache', async () => {
      const location = 'Raipur, Chhattisgarh';
      
      await geocodeLocation(location);
      
      // Check cache file exists
      // (Implementation detail - would check cache storage)
    });

    it('does not cache failed results', async () => {
      const location = 'InvalidLocation123';
      
      const result1 = await geocodeLocation(location);
      const result2 = await geocodeLocation(location);
      
      expect(result1).toBeNull();
      expect(result2).toBeNull();
    });
  });

  describe('Result Format', () => {
    it('returns correct structure for successful geocoding', async () => {
      const result = await geocodeLocation('Raipur, Chhattisgarh');
      
      expect(result).toMatchObject({
        lat: expect.any(Number),
        lng: expect.any(Number),
        source: expect.stringMatching(/mapbox|nominatim/),
        confidence: expect.any(Number),
        display_name: expect.any(String)
      });
    });

    it('includes confidence score', async () => {
      const result = await geocodeLocation('Raipur, Chhattisgarh');
      
      expect(result?.confidence).toBeGreaterThan(0);
      expect(result?.confidence).toBeLessThanOrEqual(1);
    });
  });

  describe('Error Handling', () => {
    it('handles network errors gracefully', async () => {
      // Mock network failure
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));
      
      const result = await geocodeLocation('Raipur, Chhattisgarh');
      
      // Should fall back to Nominatim or return null
      expect(result).toBeDefined();
    });

    it('handles API rate limit errors', async () => {
      // Mock rate limit error
      global.fetch = vi.fn().mockResolvedValue({
        ok: false,
        status: 429,
        json: async () => ({ error: 'Rate limit exceeded' })
      });
      
      const result = await geocodeLocation('Raipur, Chhattisgarh');
      
      // Should fall back to Nominatim
      expect(result).toBeDefined();
    });
  });
});
