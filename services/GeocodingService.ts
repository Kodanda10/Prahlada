import { ParsedLocation } from '../types';

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN || 'pk.eyJ1IjoiYWJoaWppdGEiLCJhIjoiY2x0eXF4eXF4MDI1MjJqcXF4eXF4eXF4eCJ9.dummy'; // Fallback for dev if env missing

interface GeocodeResult {
  lat: number;
  lng: number;
  display_name: string;
  source: 'mapbox' | 'nominatim' | 'cache';
  confidence: number;
}

export const GeocodingService = {
  // Exposed for testing and runtime inspection
  geocodeCache: {} as Record<string, GeocodeResult>,

  /**
   * Geocodes a location string using Mapbox (Primary) then Nominatim (Fallback)
   */
  async geocode(query: string): Promise<GeocodeResult | null> {
    if (!query) return null;

    // 1. Check Cache
    if (this.geocodeCache[query]) {
      return { ...this.geocodeCache[query], source: 'cache' };
    }

    // 2. Try Mapbox (Primary)
    try {
      const mapboxResult = await this.geocodeMapbox(query);
      if (mapboxResult) {
        this.geocodeCache[query] = mapboxResult;
        return mapboxResult;
      }
    } catch (e) {
      console.warn('Mapbox geocoding failed:', e);
    }

    // 3. Try Nominatim (Fallback)
    try {
      const nominatimResult = await this.geocodeNominatim(query);
      if (nominatimResult) {
        this.geocodeCache[query] = nominatimResult;
        return nominatimResult;
      }
    } catch (e) {
      console.warn('Nominatim geocoding failed:', e);
    }

    return null;
  },

  async geocodeMapbox(query: string): Promise<GeocodeResult | null> {
    const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${encodeURIComponent(query)}.json?access_token=${MAPBOX_TOKEN}&limit=1&country=IN`;
    
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Mapbox API error: ${res.statusText}`);
    
    const data = await res.json();
    if (data.features && data.features.length > 0) {
      const feature = data.features[0];
      return {
        lat: feature.center[1],
        lng: feature.center[0],
        display_name: feature.place_name,
        source: 'mapbox',
        confidence: feature.relevance || 0.8
      };
    }
    return null;
  },

  async geocodeNominatim(query: string): Promise<GeocodeResult | null> {
    // Nominatim requires User-Agent
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1&countrycodes=in`;
    
    const res = await fetch(url, {
      headers: {
        'User-Agent': 'Project-Prahlada-Analytics/1.0'
      }
    });
    
    if (!res.ok) throw new Error(`Nominatim API error: ${res.statusText}`);
    
    const data = await res.json();
    if (data && data.length > 0) {
      const item = data[0];
      return {
        lat: parseFloat(item.lat),
        lng: parseFloat(item.lon),
        display_name: item.display_name,
        source: 'nominatim',
        confidence: 0.7 // Nominatim doesn't provide confidence, assume moderate
      };
    }
    return null;
  },

  // Helper to get a string representation from a ParsedLocation object
  getLocationString(location: ParsedLocation): string {
    if (location.canonical) return location.canonical;
    
    const parts = [];
    if (location.village) parts.push(location.village);
    if (location.gp) parts.push(location.gp);
    if (location.block) parts.push(location.block);
    if (location.district) parts.push(location.district);
    if (location.state) parts.push(location.state || 'Chhattisgarh');
    
    return parts.join(', ');
  }
};
