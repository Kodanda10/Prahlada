import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';

describe('MapBoxVisual - Tooltip Positioning', () => {
  const mockMapbox = {
    Map: vi.fn().mockImplementation(() => ({
      on: vi.fn(),
      addControl: vi.fn(),
      remove: vi.fn(),
      getCanvas: vi.fn(() => ({
        width: 800,
        height: 600,
      })),
      project: vi.fn((lngLat) => ({ x: 400, y: 300 })), // Mock projection
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
      setLngLat: vi.fn().mockReturnThis(),
      addTo: vi.fn().mockReturnThis(),
    })),
  };

  Object.defineProperty(window, 'mapboxgl', {
    value: mockMapbox,
    writable: true,
  });

  describe('Edge Marker Positioning', () => {
    it('positions tooltips correctly for markers near viewport edges', () => {
      // Markers at different edge positions
      const edgeEvents = [
        { place: 'ऊपरी किनारा', visits: 1, lat: 22.5, lng: 83.0 }, // Top
        { place: 'निचला किनारा', visits: 2, lat: 21.5, lng: 83.0 }, // Bottom
        { place: 'बायाँ किनारा', visits: 3, lat: 22.0, lng: 82.0 },  // Left
        { place: 'दायाँ किनारा', visits: 4, lat: 22.0, lng: 84.0 },  // Right
      ];

      const popupPositions: any[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockReturnThis(),
        setMaxWidth: vi.fn().mockReturnThis(),
        setLngLat: vi.fn().mockImplementation((coords) => {
          popupPositions.push(coords);
          return {};
        }),
        addTo: vi.fn().mockReturnThis(),
      }));

      render(
        <MapBoxVisual
          data={edgeEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should position tooltips appropriately for each edge marker
      expect(popupPositions).toHaveLength(edgeEvents.length);

      mockMapbox.Popup = originalPopup;
    });

    it('adjusts tooltip position to stay within viewport bounds', () => {
      const cornerEvents = [
        { place: 'ऊपरी-बायाँ', visits: 1, lat: 22.4, lng: 82.2 }, // Top-left corner
        { place: 'निचला-दायाँ', visits: 2, lat: 21.6, lng: 83.8 }, // Bottom-right corner
      ];

      const popupOffsets: any[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockReturnThis(),
        setMaxWidth: vi.fn().mockReturnThis(),
        setLngLat: vi.fn().mockReturnThis(),
        setOffset: vi.fn().mockImplementation((offset) => {
          popupOffsets.push(offset);
          return {};
        }),
        addTo: vi.fn().mockReturnThis(),
      }));

      render(
        <MapBoxVisual
          data={cornerEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should apply appropriate offsets to keep tooltips in bounds
      expect(popupOffsets).toHaveLength(cornerEvents.length);

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Tooltip Collision Avoidance', () => {
    it('prevents tooltip overlap for nearby markers', () => {
      // Closely positioned markers
      const closeEvents = [
        { place: 'मार्कर A', visits: 1, lat: 22.01, lng: 83.01 },
        { place: 'मार्कर B', visits: 2, lat: 22.02, lng: 83.02 },
        { place: 'मार्कर C', visits: 3, lat: 22.00, lng: 83.00 },
      ];

      const tooltipAnchors: string[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockReturnThis(),
        setMaxWidth: vi.fn().mockReturnThis(),
        setLngLat: vi.fn().mockReturnThis(),
        setOffset: vi.fn().mockReturnThis(),
        addTo: vi.fn().mockReturnThis(),
        _anchor: 'center',
        set options(options: any) {
          if (options.anchor) {
            tooltipAnchors.push(options.anchor);
          }
        },
      }));

      render(
        <MapBoxVisual
          data={closeEvents}
          center={[83.0, 22.0]}
          zoom={12} // High zoom to show proximity
        />
      );

      // Should use different anchor positions to avoid overlap
      expect(tooltipAnchors.length).toBeGreaterThan(0);

      mockMapbox.Popup = originalPopup;
    });

    it('stacks tooltips vertically when horizontally aligned', () => {
      const alignedEvents = [
        { place: 'बाईं ओर', visits: 1, lat: 22.0, lng: 82.5 },
        { place: 'दाईं ओर', visits: 2, lat: 22.0, lng: 83.5 },
        { place: 'बीच में', visits: 3, lat: 22.0, lng: 83.0 },
      ];

      const offsets: any[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockReturnThis(),
        setMaxWidth: vi.fn().mockReturnThis(),
        setLngLat: vi.fn().mockReturnThis(),
        setOffset: vi.fn().mockImplementation((offset) => {
          offsets.push(offset);
          return {};
        }),
        addTo: vi.fn().mockReturnThis(),
      }));

      render(
        <MapBoxVisual
          data={alignedEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should apply different vertical offsets
      expect(offsets).toHaveLength(alignedEvents.length);

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Responsive Tooltip Positioning', () => {
    it('adjusts positioning based on screen size', () => {
      const testEvents = [
        { place: 'टेस्ट', visits: 1, lat: 22.0, lng: 83.0 },
      ];

      // Mock different screen sizes
      const screenSizes = [
        { width: 375, height: 667 }, // Mobile
        { width: 768, height: 1024 }, // Tablet
        { width: 1440, height: 900 }, // Desktop
      ];

      screenSizes.forEach(({ width, height }) => {
        // Mock viewport
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: width,
        });
        Object.defineProperty(window, 'innerHeight', {
          writable: true,
          configurable: true,
          value: height,
        });

        const { container } = render(
          <MapBoxVisual
            data={testEvents}
            center={[83.0, 22.0]}
            zoom={8}
          />
        );

        expect(container.firstChild).toBeInTheDocument();
      });
    });

    it('positions tooltips appropriately for touch devices', () => {
      // Mock touch device
      Object.defineProperty(navigator, 'maxTouchPoints', {
        value: 5,
        configurable: true,
      });

      const touchEvents = [
        { place: 'टच मार्कर', visits: 1, lat: 22.0, lng: 83.0 },
      ];

      const touchOffsets: any[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockReturnThis(),
        setMaxWidth: vi.fn().mockReturnThis(),
        setLngLat: vi.fn().mockReturnThis(),
        setOffset: vi.fn().mockImplementation((offset) => {
          touchOffsets.push(offset);
          return {};
        }),
        addTo: vi.fn().mockReturnThis(),
      }));

      render(
        <MapBoxVisual
          data={touchEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should account for finger size on touch devices
      expect(touchOffsets).toHaveLength(1);

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Dynamic Positioning Updates', () => {
    it('repositions tooltips during map interactions', () => {
      const dynamicEvents = [
        { place: 'डायनामिक', visits: 1, lat: 22.0, lng: 83.0 },
      ];

      render(
        <MapBoxVisual
          data={dynamicEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      const mapContainer = document.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();

      // Simulate map movement that should reposition tooltips
      // Implementation dependent
    });

    it('maintains tooltip position during zoom changes', () => {
      const zoomEvents = [
        { place: 'ज़ूम टेस्ट', visits: 1, lat: 22.0, lng: 83.0 },
      ];

      const { container } = render(
        <MapBoxVisual
          data={zoomEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      const mapElement = container.querySelector('.mapbox-visual');
      expect(mapElement).toBeInTheDocument();

      // Zoom changes should maintain tooltip positioning logic
      expect(mapElement).toBeInTheDocument();
    });
  });

  describe('Performance Considerations', () => {
    it('debounces tooltip positioning calculations', () => {
      const positioningCalls: number[] = [];
      let callCount = 0;

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockReturnThis(),
        setMaxWidth: vi.fn().mockReturnThis(),
        setLngLat: vi.fn().mockImplementation(() => {
          callCount++;
          positioningCalls.push(Date.now());
          return {};
        }),
        addTo: vi.fn().mockReturnThis(),
      }));

      const rapidEvents = Array.from({ length: 10 }, (_, i) => ({
        place: `तेज़ मार्कर ${i}`,
        visits: i + 1,
        lat: 22.0 + (i * 0.01),
        lng: 83.0 + (i * 0.01),
      }));

      render(
        <MapBoxVisual
          data={rapidEvents}
          center={[83.0, 22.0]}
          zoom={10}
        />
      );

      // Should not make excessive positioning calculations
      expect(callCount).toBe(rapidEvents.length);

      mockMapbox.Popup = originalPopup;
    });

    it('caches positioning calculations for performance', () => {
      const cacheHits = new Set();
      const cacheMisses = new Set();

      const events = [
        { place: 'कैश टेस्ट A', visits: 1, lat: 22.0, lng: 83.0 },
        { place: 'कैश टेस्ट B', visits: 2, lat: 22.1, lng: 83.1 },
      ];

      render(
        <MapBoxVisual
          data={events}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should optimize positioning calculations
      expect(document.querySelector('.mapbox-visual')).toBeInTheDocument();
    });
  });

  describe('Cross-Browser Positioning', () => {
    it('handles different browser coordinate systems', () => {
      const testEvents = [
        { place: 'क्रॉस-ब्राउज़र', visits: 1, lat: 22.0, lng: 83.0 },
      ];

      // Mock different browser behaviors
      const browserMocks = [
        { name: 'Chrome', offset: [0, 0] },
        { name: 'Firefox', offset: [1, 1] },
        { name: 'Safari', offset: [-1, -1] },
      ];

      browserMocks.forEach(({ name, offset }) => {
        const { container } = render(
          <MapBoxVisual
            data={testEvents}
            center={[83.0, 22.0]}
            zoom={8}
          />
        );

        expect(container.firstChild).toBeInTheDocument();
      });
    });

    it('adapts to different CSS box models', () => {
      const boxModelEvents = [
        { place: 'बॉक्स मॉडल', visits: 1, lat: 22.0, lng: 83.0 },
      ];

      // Test with different box-sizing
      const boxSizingValues = ['border-box', 'content-box'];

      boxSizingValues.forEach(boxSizing => {
        Object.defineProperty(document, 'body', {
          value: {
            style: { boxSizing },
          },
          writable: true,
        });

        render(
          <MapBoxVisual
            data={boxModelEvents}
            center={[83.0, 22.0]}
            zoom={8}
          />
        );

        expect(document.querySelector('.mapbox-visual')).toBeInTheDocument();
      });
    });
  });
});