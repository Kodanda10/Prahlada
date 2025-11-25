import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { GeocodingService } from '../../services/GeocodingService';
import realData from '../../data/ingested_tweets.json';

describe('GeocodingService', () => {
  const sampleLocation = 'Raipur, Chhattisgarh';

  beforeEach(() => {
    // Use stubGlobal for fetch to ensure it works in jsdom environment
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    vi.spyOn(console, 'warn').mockImplementation(() => {});
    
    // Clear cache before each test
    GeocodingService.geocodeCache = {};
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it('returns cached result if available', async () => {
    // Seed cache
    GeocodingService.geocodeCache = {
      [sampleLocation]: { lat: 21.25, lng: 81.63, source: 'cache', display_name: 'Cached', confidence: 1 }
    };

    const result = await GeocodingService.geocode(sampleLocation);
    expect(result).toEqual(expect.objectContaining({
      lat: 21.25,
      lng: 81.63,
      source: 'cache'
    }));
    expect(fetch).not.toHaveBeenCalled();
  });

  it('calls Mapbox (Primary) first', async () => {
    const mockMapboxResponse = {
      features: [{
        center: [81.63, 21.25],
        place_name: 'Raipur, Chhattisgarh, India',
        relevance: 0.9
      }]
    };

    (fetch as any).mockResolvedValueOnce({
      ok: true,
      json: async () => mockMapboxResponse
    });

    const result = await GeocodingService.geocode(sampleLocation);

    expect(fetch).toHaveBeenCalledTimes(1);
    // Mapbox call has no options
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('api.mapbox.com'));
    expect(result).toEqual(expect.objectContaining({
      lat: 21.25,
      lng: 81.63,
      source: 'mapbox'
    }));
  });

  it('falls back to Nominatim if Mapbox fails', async () => {
    // Mapbox fails (mock rejection)
    (fetch as any)
      .mockRejectedValueOnce(new Error('Mapbox Error'))
      // Nominatim succeeds
      .mockResolvedValueOnce({
        ok: true,
        json: async () => [{
          lat: '21.2514',
          lon: '81.6296',
          display_name: 'Raipur, Chhattisgarh, India'
        }]
      });

    const result = await GeocodingService.geocode(sampleLocation);

    expect(fetch).toHaveBeenCalledTimes(2);
    expect(fetch).toHaveBeenNthCalledWith(1, expect.stringContaining('api.mapbox.com'));
    expect(fetch).toHaveBeenNthCalledWith(2, expect.stringContaining('nominatim.openstreetmap.org'), expect.anything());
    
    expect(result).toEqual(expect.objectContaining({
      lat: 21.2514,
      lng: 81.6296,
      source: 'nominatim'
    }));
  });

  it('handles real location data from tweets', async () => {
    // Find a tweet with a location that is NOT null and has a district
    const tweet = realData.find(t => t.parsed_data_v8?.location?.district);
    
    if (!tweet) {
      console.warn('No tweet with valid location found in sample data');
      return;
    }

    const locationStr = GeocodingService.getLocationString(tweet.parsed_data_v8.location);
    expect(locationStr).toBeTruthy();

    // Mock success
    (fetch as any).mockResolvedValue({
      ok: true,
      json: async () => ({ features: [{ center: [0, 0], place_name: 'Test' }] })
    });

    await GeocodingService.geocode(locationStr);
    expect(fetch).toHaveBeenCalled();
  });
});
