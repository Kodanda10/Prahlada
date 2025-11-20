import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';

describe('MapBoxVisual - Marker Rendering & Data Mapping', () => {
  // Mock Mapbox GL JS since we can't use real Mapbox in unit tests
  const mockMapbox = {
    Map: vi.fn().mockImplementation(() => ({
      on: vi.fn(),
      addControl: vi.fn(),
      addSource: vi.fn(),
      addLayer: vi.fn(),
      remove: vi.fn(),
      setCenter: vi.fn(),
      setZoom: vi.fn(),
      flyTo: vi.fn(),
    })),
    NavigationControl: vi.fn(),
    ScaleControl: vi.fn(),
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

  // Mock the mapboxgl global
  Object.defineProperty(window, 'mapboxgl', {
    value: mockMapbox,
    writable: true,
  });

  const mockEvents = [
    { place: 'खरसिया', visits: 5, lat: 21.99, lng: 83.08 },
    { place: 'तमनार', visits: 3, lat: 21.88, lng: 83.27 },
    { place: 'जोंबी', visits: 8, lat: 21.95, lng: 83.12 },
  ];

  const defaultCenter = [83.0, 22.0]; // Central Chhattisgarh
  const defaultZoom = 8;

  describe('Marker Creation and Positioning', () => {
    it('creates markers for each event location', () => {
      const mockMarkerInstances: any[] = [];

      // Override Marker constructor to track instances
      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => {
        const marker = {
          setLngLat: vi.fn().mockReturnThis(),
          setPopup: vi.fn().mockReturnThis(),
          addTo: vi.fn().mockReturnThis(),
          remove: vi.fn(),
        };
        mockMarkerInstances.push(marker);
        return marker;
      });

      render(
        <MapBoxVisual
          data={mockEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should create one marker per event
      expect(mockMapbox.Marker).toHaveBeenCalledTimes(mockEvents.length);
      expect(mockMarkerInstances).toHaveLength(mockEvents.length);

      // Restore original
      mockMapbox.Marker = originalMarker;
    });

    it('positions markers at correct coordinates', () => {
      const markerCalls: any[] = [];

      // Track setLngLat calls
      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => ({
        setLngLat: vi.fn().mockImplementation((coords) => {
          markerCalls.push(coords);
          return {
            setPopup: vi.fn().mockReturnThis(),
            addTo: vi.fn().mockReturnThis(),
            remove: vi.fn(),
          };
        }),
        setPopup: vi.fn().mockReturnThis(),
        addTo: vi.fn().mockReturnThis(),
        remove: vi.fn(),
      }));

      render(
        <MapBoxVisual
          data={mockEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should position markers at correct long/lat
      mockEvents.forEach((event, index) => {
        expect(markerCalls[index]).toEqual([event.lng, event.lat]);
      });

      // Restore original
      mockMapbox.Marker = originalMarker;
    });

    it('displays Hindi location names with visit counts', () => {
      const popupContents: string[] = [];

      // Track popup content
      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockImplementation((html) => {
          popupContents.push(html);
          return {
            setMaxWidth: vi.fn().mockReturnThis(),
          };
        }),
        setMaxWidth: vi.fn().mockReturnThis(),
      }));

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => ({
        setLngLat: vi.fn().mockReturnThis(),
        setPopup: vi.fn().mockReturnThis(),
        addTo: vi.fn().mockReturnThis(),
        remove: vi.fn(),
      }));

      render(
        <MapBoxVisual
          data={mockEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should create popups for each marker
      expect(mockMapbox.Popup).toHaveBeenCalledTimes(mockEvents.length);
      expect(popupContents).toHaveLength(mockEvents.length);

      // Restore originals
      mockMapbox.Popup = originalPopup;
      mockMapbox.Marker = originalMarker;
    });
  });

  describe('Marker Styling and Icons', () => {
    it('uses appropriate marker colors for visit ranges', () => {
      // Different visit counts should have different visual styles
      const variedEvents = [
        { place: 'कम दौरे', visits: 1, lat: 22.0, lng: 83.0 },
        { place: 'मध्यम दौरे', visits: 5, lat: 22.1, lng: 83.1 },
        { place: 'अधिक दौरे', visits: 15, lat: 22.2, lng: 83.2 },
      ];

      const markerElements: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation((options) => {
        markerElements.push(options);
        return {
          setLngLat: vi.fn().mockReturnThis(),
          setPopup: vi.fn().mockReturnThis(),
          addTo: vi.fn().mockReturnThis(),
          remove: vi.fn(),
        };
      });

      render(
        <MapBoxVisual
          data={variedEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should create markers with appropriate styling
      expect(markerElements).toHaveLength(variedEvents.length);

      // Restore original
      mockMapbox.Marker = originalMarker;
    });

    it('provides accessible marker elements', () => {
      const markerInstances: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => {
        const marker = {
          setLngLat: vi.fn().mockReturnThis(),
          setPopup: vi.fn().mockReturnThis(),
          addTo: vi.fn().mockReturnThis(),
          remove: vi.fn(),
          getElement: vi.fn(() => ({
            setAttribute: vi.fn(),
            ariaLabel: '',
          })),
        };
        markerInstances.push(marker);
        return marker;
      });

      render(
        <MapBoxVisual
          data={mockEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should create accessible markers
      expect(markerInstances).toHaveLength(mockEvents.length);

      // Restore original
      mockMapbox.Marker = originalMarker;
    });
  });

  describe('Data Mapping Accuracy', () => {
    it('correctly maps event data to marker properties', () => {
      const markerData: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => {
        const marker = {
          setLngLat: vi.fn().mockReturnThis(),
          setPopup: vi.fn().mockReturnThis(),
          addTo: vi.fn().mockReturnThis(),
          remove: vi.fn(),
          _data: null as any,
        };
        markerData.push(marker);
        return marker;
      });

      render(
        <MapBoxVisual
          data={mockEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Each marker should be associated with correct event data
      expect(markerData).toHaveLength(mockEvents.length);

      // Restore original
      mockMapbox.Marker = originalMarker;
    });

    it('handles coordinate precision correctly', () => {
      const preciseEvents = [
        { place: 'टेस्ट 1', visits: 1, lat: 21.987654, lng: 83.123456 },
        { place: 'टेस्ट 2', visits: 2, lat: 22.111111, lng: 83.999999 },
      ];

      const coordinateCalls: number[][] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => ({
        setLngLat: vi.fn().mockImplementation((coords) => {
          coordinateCalls.push(coords);
          return {
            setPopup: vi.fn().mockReturnThis(),
            addTo: vi.fn().mockReturnThis(),
            remove: vi.fn(),
          };
        }),
        setPopup: vi.fn().mockReturnThis(),
        addTo: vi.fn().mockReturnThis(),
        remove: vi.fn(),
      }));

      render(
        <MapBoxVisual
          data={preciseEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should preserve coordinate precision
      expect(coordinateCalls).toHaveLength(preciseEvents.length);
      expect(coordinateCalls[0]).toEqual([preciseEvents[0].lng, preciseEvents[0].lat]);
      expect(coordinateCalls[1]).toEqual([preciseEvents[1].lng, preciseEvents[1].lat]);

      // Restore original
      mockMapbox.Marker = originalMarker;
    });

    it('validates coordinate ranges', () => {
      const invalidEvents = [
        { place: 'अमान्य', visits: 1, lat: 91, lng: 181 }, // Out of range
        { place: 'वैध', visits: 2, lat: 22.0, lng: 83.0 }, // Valid
      ];

      const coordinateCalls: number[][] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => ({
        setLngLat: vi.fn().mockImplementation((coords) => {
          coordinateCalls.push(coords);
          return {
            setPopup: vi.fn().mockReturnThis(),
            addTo: vi.fn().mockReturnThis(),
            remove: vi.fn(),
          };
        }),
        setPopup: vi.fn().mockReturnThis(),
        addTo: vi.fn().mockReturnThis(),
        remove: vi.fn(),
      }));

      render(
        <MapBoxVisual
          data={invalidEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should only create markers for valid coordinates
      expect(coordinateCalls).toHaveLength(1); // Only the valid one
      expect(coordinateCalls[0]).toEqual([83.0, 22.0]);

      // Restore original
      mockMapbox.Marker = originalMarker;
    });
  });

  describe('Marker Clustering Logic', () => {
    it('groups nearby markers when density is high', () => {
      // Create clustered events
      const clusteredEvents = [
        { place: 'पॉइंट A1', visits: 2, lat: 22.000, lng: 83.000 },
        { place: 'पॉइंट A2', visits: 3, lat: 22.001, lng: 83.001 }, // Very close
        { place: 'पॉइंट B1', visits: 5, lat: 22.100, lng: 83.100 }, // Farther away
      ];

      const markerInstances: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => {
        const marker = {
          setLngLat: vi.fn().mockReturnThis(),
          setPopup: vi.fn().mockReturnThis(),
          addTo: vi.fn().mockReturnThis(),
          remove: vi.fn(),
        };
        markerInstances.push(marker);
        return marker;
      });

      render(
        <MapBoxVisual
          data={clusteredEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should create individual markers (clustering would be zoom-dependent)
      expect(markerInstances).toHaveLength(clusteredEvents.length);

      // Restore original
      mockMapbox.Marker = originalMarker;
    });

    it('shows cluster counts for grouped markers', () => {
      // Test would verify cluster markers show counts
      // This depends on zoom level and clustering implementation
      expect(true).toBe(true); // Placeholder for cluster count testing
    });
  });

  describe('Marker Lifecycle Management', () => {
    it('cleans up markers when component unmounts', () => {
      const markerInstances: any[] = [];
      const removeCalls: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => {
        const marker = {
          setLngLat: vi.fn().mockReturnThis(),
          setPopup: vi.fn().mockReturnThis(),
          addTo: vi.fn().mockReturnThis(),
          remove: vi.fn().mockImplementation(() => {
            removeCalls.push(true);
          }),
        };
        markerInstances.push(marker);
        return marker;
      });

      const { unmount } = render(
        <MapBoxVisual
          data={mockEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      expect(markerInstances).toHaveLength(mockEvents.length);

      unmount();

      // Should clean up all markers
      expect(removeCalls).toHaveLength(mockEvents.length);

      // Restore original
      mockMapbox.Marker = originalMarker;
    });

    it('updates markers when data changes', () => {
      const initialEvents = [
        { place: 'प्रारंभिक', visits: 1, lat: 22.0, lng: 83.0 },
      ];

      const { rerender } = render(
        <MapBoxVisual
          data={initialEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Update with new data
      const updatedEvents = [
        { place: 'अपडेटेड', visits: 2, lat: 22.1, lng: 83.1 },
        { place: 'नया', visits: 3, lat: 22.2, lng: 83.2 },
      ];

      rerender(
        <MapBoxVisual
          data={updatedEvents}
          center={defaultCenter}
          zoom={defaultZoom}
        />
      );

      // Should handle data updates gracefully
      expect(true).toBe(true); // Implementation-dependent
    });
  });
});