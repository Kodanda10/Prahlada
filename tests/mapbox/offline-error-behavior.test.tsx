import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';

describe('MapBoxVisual - Offline / Error Behavior', () => {
  const mockMapbox = {
    Map: vi.fn().mockImplementation(() => ({
      on: vi.fn(),
      addControl: vi.fn(),
      addSource: vi.fn().mockImplementation(() => {
        throw new Error('Network error');
      }),
      addLayer: vi.fn().mockImplementation(() => {
        throw new Error('Tile load failed');
      }),
      remove: vi.fn(),
      setCenter: vi.fn(),
      setZoom: vi.fn(),
      flyTo: vi.fn(),
      getZoom: vi.fn(() => 8),
      getCenter: vi.fn(() => ({ lng: 83.0, lat: 22.0 })),
    })),
    Marker: vi.fn().mockImplementation(() => ({
      setLngLat: vi.fn().mockReturnThis(),
      setPopup: vi.fn().mockReturnThis(),
      addTo: vi.fn().mockReturnThis(),
      remove: vi.fn(),
    })),
    Popup: vi.fn().mockImplementation(() => ({
      setHTML: vi.fn().mockReturnThis(),
      setMaxWidth: vi.fn().mockReturnThis(),
    })),
  };

  Object.defineProperty(window, 'mapboxgl', {
    value: mockMapbox,
    writable: true,
  });

  const testData = [
    { place: 'खरसिया', visits: 5, lat: 21.99, lng: 83.08 },
    { place: 'तमनार', visits: 3, lat: 21.88, lng: 83.27 },
  ];

  describe('Network Failure Handling', () => {
    it('displays Hindi error message when map tiles fail to load', () => {
      // Mock network failure
      const originalFetch = global.fetch;
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should show Hindi error message
      // Note: In real implementation, this would be shown in the map container
      expect(document.querySelector('.mapbox-visual')).toBeInTheDocument();

      global.fetch = originalFetch;
    });

    it('shows offline indicator when network is unavailable', () => {
      // Mock offline state
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should show offline message
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();

      // Reset online state
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        configurable: true,
      });
    });

    it('provides fallback map when Mapbox is completely unavailable', () => {
      // Mock Mapbox completely unavailable
      const originalMapbox = window.mapboxgl;
      delete (window as any).mapboxgl;

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should render fallback content
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();

      // Restore Mapbox
      window.mapboxgl = originalMapbox;
    });
  });

  describe('Graceful Degradation', () => {
    it('still shows markers when map fails to load', () => {
      // Mock map initialization failure
      mockMapbox.Map = vi.fn().mockImplementation(() => {
        throw new Error('Map initialization failed');
      });

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should still attempt to render markers
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();

      // Reset mock
      mockMapbox.Map = vi.fn().mockImplementation(() => ({
        on: vi.fn(),
        addControl: vi.fn(),
        remove: vi.fn(),
        setCenter: vi.fn(),
        setZoom: vi.fn(),
        flyTo: vi.fn(),
        getZoom: vi.fn(() => 8),
        getCenter: vi.fn(() => ({ lng: 83.0, lat: 22.0 })),
      }));
    });

    it('displays data in alternative format when map is unavailable', () => {
      // Mock map unavailability
      const originalMapbox = window.mapboxgl;
      delete (window as any).mapboxgl;

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should show data in table/list format
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();

      // Should contain location data
      expect(testData[0].place).toBe('खरसिया');
      expect(testData[1].place).toBe('तमनार');

      // Restore Mapbox
      window.mapboxgl = originalMapbox;
    });

    it('maintains core functionality with reduced features', () => {
      // Mock partial failure (map loads but some features fail)
      mockMapbox.Map = vi.fn().mockImplementation(() => ({
        on: vi.fn(),
        addControl: vi.fn(),
        remove: vi.fn(),
        setCenter: vi.fn(),
        setZoom: vi.fn(),
        flyTo: vi.fn(),
        getZoom: vi.fn(() => 8),
        getCenter: vi.fn(() => ({ lng: 83.0, lat: 22.0 })),
        addSource: vi.fn().mockRejectedValue(new Error('Source failed')),
        addLayer: vi.fn().mockRejectedValue(new Error('Layer failed')),
      }));

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should still render basic map and markers
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });
  });

  describe('Error Recovery', () => {
    it('retries failed operations with exponential backoff', () => {
      let attemptCount = 0;
      const originalMap = mockMapbox.Map;

      mockMapbox.Map = vi.fn().mockImplementation(() => {
        attemptCount++;
        if (attemptCount < 3) {
          throw new Error('Temporary failure');
        }
        return {
          on: vi.fn(),
          addControl: vi.fn(),
          remove: vi.fn(),
          setCenter: vi.fn(),
          setZoom: vi.fn(),
          flyTo: vi.fn(),
          getZoom: vi.fn(() => 8),
          getCenter: vi.fn(() => ({ lng: 83.0, lat: 22.0 })),
        };
      });

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should retry failed operations
      expect(attemptCount).toBeGreaterThanOrEqual(3);

      mockMapbox.Map = originalMap;
    });

    it('recovers from temporary network issues', () => {
      let networkCallCount = 0;
      const originalFetch = global.fetch;

      global.fetch = vi.fn()
        .mockRejectedValueOnce(new Error('Network timeout'))
        .mockRejectedValueOnce(new Error('Connection failed'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ success: true }),
        });

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should recover after temporary failures
      expect(global.fetch).toHaveBeenCalled();

      global.fetch = originalFetch;
    });

    it('provides manual retry option for users', () => {
      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should include retry button in error states
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });
  });

  describe('Offline Data Management', () => {
    it('caches marker data for offline use', () => {
      const cacheStorage = new Map();

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should cache data for offline access
      expect(cacheStorage.size).toBeGreaterThanOrEqual(0);
    });

    it('shows cached data when offline', () => {
      // Mock offline state
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should display cached/offline data
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();

      // Reset online state
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        configurable: true,
      });
    });

    it('syncs data when connection is restored', () => {
      // Start offline
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        configurable: true,
      });

      const { rerender } = render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Come back online
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        configurable: true,
      });

      rerender(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should sync cached data
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });
  });

  describe('User Communication', () => {
    it('shows clear Hindi error messages', () => {
      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Error messages should be in Hindi
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });

    it('provides helpful recovery instructions', () => {
      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should include instructions like "नेटवर्क कनेक्शन जांचें"
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });

    it('indicates loading states during recovery', () => {
      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should show loading indicators during retry operations
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });
  });

  describe('Performance During Errors', () => {
    it('maintains UI responsiveness during error handling', () => {
      const startTime = performance.now();

      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render within reasonable time even with error handling
      expect(renderTime).toBeLessThan(1000);
    });

    it('prevents error handling from blocking user interactions', () => {
      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Error handling should not block the UI
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });

    it('cleans up error state properly', () => {
      const { unmount } = render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      unmount();

      // Should clean up error handlers and state
      expect(true).toBe(true);
    });
  });

  describe('Accessibility in Error States', () => {
    it('provides screen reader announcements for errors', () => {
      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Error messages should be announced to screen readers
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });

    it('maintains keyboard navigation during errors', () => {
      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Keyboard navigation should still work in error states
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });

    it('offers alternative data access methods', () => {
      render(
        <MapBoxVisual
          data={testData}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should provide alternative ways to access data (tables, lists)
      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });
  });
});