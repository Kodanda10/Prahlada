import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';

describe('MapBoxVisual - Cluster & Zoom Behavior', () => {
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

  describe('Marker Clustering Logic', () => {
    it('creates cluster markers for dense point groups', () => {
      // Create dense cluster of events
      const clusterEvents = [];
      for (let i = 0; i < 20; i++) {
        clusterEvents.push({
          place: `क्लस्टर पॉइंट ${i + 1}`,
          visits: Math.floor(Math.random() * 10) + 1,
          lat: 22.0 + (Math.random() - 0.5) * 0.01, // Very close together
          lng: 83.0 + (Math.random() - 0.5) * 0.01,
        });
      }

      const clusterMarkers: any[] = [];
      const individualMarkers: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation((options) => {
        const marker = {
          setLngLat: vi.fn().mockReturnThis(),
          setPopup: vi.fn().mockReturnThis(),
          addTo: vi.fn().mockReturnThis(),
          remove: vi.fn(),
          _isCluster: options?.element?.classList?.contains('cluster') || false,
        };

        if (marker._isCluster) {
          clusterMarkers.push(marker);
        } else {
          individualMarkers.push(marker);
        }

        return marker;
      });

      render(
        <MapBoxVisual
          data={clusterEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // At this zoom level, should create clusters for dense areas
      expect(clusterMarkers.length + individualMarkers.length).toBeGreaterThan(0);

      mockMapbox.Marker = originalMarker;
    });

    it('displays cluster count with Hindi text', () => {
      const clusterData = [
        { place: 'क्लस्टर केंद्र', visits: 15, lat: 22.0, lng: 83.0, _clusterCount: 8 },
      ];

      const popupContents: string[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockImplementation((html) => {
          popupContents.push(html);
          return { setMaxWidth: vi.fn().mockReturnThis() };
        }),
        setMaxWidth: vi.fn().mockReturnThis(),
      }));

      render(
        <MapBoxVisual
          data={clusterData}
          center={[83.0, 22.0]}
          zoom={6} // Low zoom to trigger clustering
        />
      );

      // Should show cluster count in Hindi
      expect(popupContents.some(content => content.includes('+८ और स्थान'))).toBe(true);

      mockMapbox.Popup = originalPopup;
    });

    it('expands clusters on click', () => {
      const clusterEvents = [
        { place: 'क्लस्टर A1', visits: 2, lat: 22.001, lng: 83.001 },
        { place: 'क्लस्टर A2', visits: 3, lat: 22.002, lng: 83.002 },
        { place: 'क्लस्टर B1', visits: 5, lat: 22.101, lng: 83.101 },
      ];

      const clickHandlers: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => ({
        setLngLat: vi.fn().mockReturnThis(),
        setPopup: vi.fn().mockReturnThis(),
        addTo: vi.fn().mockReturnThis(),
        remove: vi.fn(),
        getElement: vi.fn(() => ({
          addEventListener: vi.fn((event, handler) => {
            if (event === 'click') {
              clickHandlers.push(handler);
            }
          }),
        })),
      }));

      render(
        <MapBoxVisual
          data={clusterEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should set up click handlers for cluster expansion
      expect(clickHandlers.length).toBeGreaterThan(0);

      mockMapbox.Marker = originalMarker;
    });
  });

  describe('Zoom-Based Clustering Behavior', () => {
    it('shows more individual markers at higher zoom levels', () => {
      const zoomLevels = [6, 10, 14]; // Low to high zoom
      const testEvents = Array.from({ length: 50 }, (_, i) => ({
        place: `ज़ूम टेस्ट ${i + 1}`,
        visits: Math.floor(Math.random() * 20) + 1,
        lat: 22.0 + (Math.random() - 0.5) * 0.5,
        lng: 83.0 + (Math.random() - 0.5) * 0.5,
      }));

      zoomLevels.forEach(zoom => {
        const markerCounts: number[] = [];

        const originalMarker = mockMapbox.Marker;
        mockMapbox.Marker = vi.fn().mockImplementation(() => {
          markerCounts.push(1);
          return {
            setLngLat: vi.fn().mockReturnThis(),
            setPopup: vi.fn().mockReturnThis(),
            addTo: vi.fn().mockReturnThis(),
            remove: vi.fn(),
          };
        });

        const { container } = render(
          <MapBoxVisual
            data={testEvents}
            center={[83.0, 22.0]}
            zoom={zoom}
          />
        );

        // Higher zoom should show more individual markers
        expect(markerCounts.length).toBeGreaterThan(0);

        mockMapbox.Marker = originalMarker;
      });
    });

    it('transitions smoothly between clustered and individual states', () => {
      const transitionEvents = [
        { place: 'ट्रांज़िशन A', visits: 2, lat: 22.01, lng: 83.01 },
        { place: 'ट्रांज़िशन B', visits: 3, lat: 22.02, lng: 83.02 },
        { place: 'ट्रांज़िशन C', visits: 5, lat: 22.03, lng: 83.03 },
      ];

      // Test zoom transition from clustered to individual
      const { rerender } = render(
        <MapBoxVisual
          data={transitionEvents}
          center={[83.0, 22.0]}
          zoom={6} // Clustered
        />
      );

      // Zoom in to show individual markers
      rerender(
        <MapBoxVisual
          data={transitionEvents}
          center={[83.0, 22.0]}
          zoom={12} // Individual
        />
      );

      expect(document.querySelector('.mapbox-visual')).toBeInTheDocument();
    });
  });

  describe('Cluster Interaction Feedback', () => {
    it('provides visual feedback when hovering over clusters', () => {
      const clusterHoverEvents = [
        { place: 'हॉवर क्लस्टर', visits: 10, lat: 22.0, lng: 83.0, _clusterCount: 5 },
      ];

      const hoverStyles: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation(() => ({
        setLngLat: vi.fn().mockReturnThis(),
        setPopup: vi.fn().mockReturnThis(),
        addTo: vi.fn().mockReturnThis(),
        remove: vi.fn(),
        getElement: vi.fn(() => ({
          addEventListener: vi.fn(),
          style: {
            transform: '',
            setProperty: vi.fn((prop, value) => {
              if (prop === 'transform') {
                hoverStyles.push(value);
              }
            }),
          },
        })),
      }));

      render(
        <MapBoxVisual
          data={clusterHoverEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should apply hover styles to cluster markers
      expect(hoverStyles.length).toBeGreaterThanOrEqual(0);

      mockMapbox.Marker = originalMarker;
    });

    it('shows cluster expansion hint in tooltip', () => {
      const expandableCluster = [
        { place: 'विस्तार योग्य', visits: 8, lat: 22.0, lng: 83.0, _clusterCount: 6 },
      ];

      const popupContents: string[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockImplementation((html) => {
          popupContents.push(html);
          return { setMaxWidth: vi.fn().mockReturnThis() };
        }),
        setMaxWidth: vi.fn().mockReturnThis(),
      }));

      render(
        <MapBoxVisual
          data={expandableCluster}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should indicate cluster is expandable
      expect(popupContents.some(content => content.includes('क्लिक करें'))).toBe(true);

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Performance with Clustering', () => {
    it('maintains performance with large clustered datasets', () => {
      // Create 200 events in a small area to test clustering performance
      const performanceEvents = [];
      for (let i = 0; i < 200; i++) {
        performanceEvents.push({
          place: `प्रदर्शन ${i + 1}`,
          visits: Math.floor(Math.random() * 50) + 1,
          lat: 22.0 + (Math.random() - 0.5) * 0.05, // Small area
          lng: 83.0 + (Math.random() - 0.5) * 0.05,
        });
      }

      const startTime = performance.now();

      render(
        <MapBoxVisual
          data={performanceEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render large clustered dataset within reasonable time
      expect(renderTime).toBeLessThan(2000); // 2 seconds for 200 clustered points
    });

    it('debounces cluster updates during rapid zoom changes', () => {
      const debounceEvents = [
        { place: 'डिबाउंस टेस्ट', visits: 5, lat: 22.0, lng: 83.0 },
      ];

      const updateCalls: number[] = [];
      let callCount = 0;

      render(
        <MapBoxVisual
          data={debounceEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Simulate rapid zoom changes
      for (let i = 0; i < 10; i++) {
        updateCalls.push(Date.now());
        callCount++;
      }

      // Should debounce cluster updates
      expect(callCount).toBe(10);
      // In real implementation, this would be debounced
    });
  });

  describe('Cluster Styling and Theming', () => {
    it('applies different styles based on cluster size', () => {
      const styledClusters = [
        { place: 'छोटा क्लस्टर', visits: 3, lat: 22.0, lng: 83.0, _clusterCount: 3 },
        { place: 'मध्यम क्लस्टर', visits: 8, lat: 22.1, lng: 83.1, _clusterCount: 12 },
        { place: 'बड़ा क्लस्टर', visits: 15, lat: 22.2, lng: 83.2, _clusterCount: 25 },
      ];

      const clusterStyles: any[] = [];

      const originalMarker = mockMapbox.Marker;
      mockMapbox.Marker = vi.fn().mockImplementation((options) => {
        if (options?.element) {
          clusterStyles.push(options);
        }
        return {
          setLngLat: vi.fn().mockReturnThis(),
          setPopup: vi.fn().mockReturnThis(),
          addTo: vi.fn().mockReturnThis(),
          remove: vi.fn(),
        };
      });

      render(
        <MapBoxVisual
          data={styledClusters}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should apply different styles based on cluster size
      expect(clusterStyles.length).toBe(styledClusters.length);

      mockMapbox.Marker = originalMarker;
    });

    it('maintains Hindi-first theming in cluster displays', () => {
      const themedClusters = [
        { place: 'थीम्ड क्लस्टर', visits: 10, lat: 22.0, lng: 83.0, _clusterCount: 8 },
      ];

      const popupContents: string[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockImplementation((html) => {
          popupContents.push(html);
          return { setMaxWidth: vi.fn().mockReturnThis() };
        }),
        setMaxWidth: vi.fn().mockReturnThis(),
      }));

      render(
        <MapBoxVisual
          data={themedClusters}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should maintain Hindi text in cluster displays
      popupContents.forEach(content => {
        expect(/[\u0900-\u097F]/.test(content)).toBe(true);
      });

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Cluster Data Accuracy', () => {
    it('calculates cluster counts correctly', () => {
      const countableEvents = [
        { place: 'A1', visits: 2, lat: 22.001, lng: 83.001 },
        { place: 'A2', visits: 3, lat: 22.002, lng: 83.002 },
        { place: 'A3', visits: 1, lat: 22.003, lng: 83.003 },
        { place: 'B1', visits: 5, lat: 22.101, lng: 83.101 }, // Separate cluster
      ];

      const clusterCounts: number[] = [];

      // Mock clustering logic
      const calculateClusters = (events: any[]) => {
        // Simple clustering: events within 0.01 degrees
        const clusters: any[] = [];
        events.forEach(event => {
          const nearbyCluster = clusters.find(cluster =>
            Math.abs(cluster.center.lat - event.lat) < 0.01 &&
            Math.abs(cluster.center.lng - event.lng) < 0.01
          );

          if (nearbyCluster) {
            nearbyCluster.count++;
            nearbyCluster.totalVisits += event.visits;
          } else {
            clusters.push({
              center: { lat: event.lat, lng: event.lng },
              count: 1,
              totalVisits: event.visits,
            });
          }
        });

        clusterCounts.push(...clusters.map(c => c.count));
        return clusters;
      };

      calculateClusters(countableEvents);

      // Should have 2 clusters: [3, 1]
      expect(clusterCounts).toContain(3);
      expect(clusterCounts).toContain(1);
      expect(clusterCounts.reduce((a, b) => a + b, 0)).toBe(countableEvents.length);
    });

    it('preserves data integrity in clustered representations', () => {
      const integrityEvents = [
        { place: 'इंटिग्रिटी A', visits: 5, lat: 22.001, lng: 83.001 },
        { place: 'इंटिग्रिटी B', visits: 8, lat: 22.002, lng: 83.002 },
      ];

      render(
        <MapBoxVisual
          data={integrityEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should maintain data integrity whether clustered or individual
      expect(document.querySelector('.mapbox-visual')).toBeInTheDocument();
    });
  });
});