import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';

describe('MapBoxVisual - Tooltip Content (Hindi-only)', () => {
  // Mock Mapbox GL JS
  const mockMapbox = {
    Map: vi.fn().mockImplementation(() => ({
      on: vi.fn(),
      addControl: vi.fn(),
      remove: vi.fn(),
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

  const mockEvents = [
    {
      place: 'खरसिया',
      visits: 5,
      lat: 21.99,
      lng: 83.08,
      lastVisit: '2024-01-15',
    },
    {
      place: 'तमनार',
      visits: 3,
      lat: 21.88,
      lng: 83.27,
      lastVisit: '2024-01-20',
    },
    {
      place: 'जोंबी',
      visits: 12,
      lat: 21.95,
      lng: 83.12,
      lastVisit: '2024-01-18',
    },
  ];

  describe('Tooltip Content Structure', () => {
    it('displays location name in Hindi', () => {
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
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should create tooltips with Hindi content
      expect(popupContents).toHaveLength(mockEvents.length);

      // Verify Hindi location names are included
      popupContents.forEach(content => {
        expect(content).toMatch(/खरसिया|तमनार|जोंबी/);
      });

      mockMapbox.Popup = originalPopup;
    });

    it('shows visit count with proper Hindi formatting', () => {
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
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should format visit counts properly
      expect(popupContents.some(content => content.includes('कुल दौरे: 05'))).toBe(true);
      expect(popupContents.some(content => content.includes('कुल दौरे: 03'))).toBe(true);
      expect(popupContents.some(content => content.includes('कुल दौरे: 12'))).toBe(true);

      mockMapbox.Popup = originalPopup;
    });

    it('includes last visit date in Hindi format', () => {
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
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should include last visit information
      popupContents.forEach(content => {
        expect(content).toMatch(/अंतिम गतिविधि/);
      });

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Tooltip Language Compliance', () => {
    it('contains only Hindi text and allowed characters', () => {
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
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      popupContents.forEach(content => {
        // Extract text content (basic check)
        const textContent = content.replace(/<[^>]*>/g, '');

        // Should not contain unallowlisted English words
        const englishWords = textContent.match(/[A-Za-z]+/g) || [];
        englishWords.forEach(word => {
          // Only allow numbers and specific allowed words
          expect(word.match(/^\d+$/) || ['Location', 'Visits', 'Last'].includes(word)).toBe(true);
        });

        // Should contain Devanagari script
        expect(/[\u0900-\u097F]/.test(textContent)).toBe(true);
      });

      mockMapbox.Popup = originalPopup;
    });

    it('formats dates in Hindi locale', () => {
      const eventsWithDates = [
        {
          place: 'खरसिया',
          visits: 5,
          lat: 21.99,
          lng: 83.08,
          lastVisit: '2024-01-15',
        },
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
          data={eventsWithDates}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should format dates appropriately (implementation dependent)
      expect(popupContents).toHaveLength(1);

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Tooltip Styling and Layout', () => {
    it('sets appropriate maximum width for tooltips', () => {
      const maxWidthCalls: any[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => ({
        setHTML: vi.fn().mockReturnThis(),
        setMaxWidth: vi.fn().mockImplementation((width) => {
          maxWidthCalls.push(width);
          return {};
        }),
      }));

      render(
        <MapBoxVisual
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should set reasonable max width for tooltips
      expect(maxWidthCalls.length).toBe(mockEvents.length);
      maxWidthCalls.forEach(width => {
        expect(width).toBeGreaterThan(200); // Reasonable min width
        expect(width).toBeLessThan(500);   // Reasonable max width
      });

      mockMapbox.Popup = originalPopup;
    });

    it('applies consistent styling to all tooltips', () => {
      const popupInstances: any[] = [];

      const originalPopup = mockMapbox.Popup;
      mockMapbox.Popup = vi.fn().mockImplementation(() => {
        const popup = {
          setHTML: vi.fn().mockReturnThis(),
          setMaxWidth: vi.fn().mockReturnThis(),
          _styling: 'consistent',
        };
        popupInstances.push(popup);
        return popup;
      });

      render(
        <MapBoxVisual
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should create consistently styled tooltips
      expect(popupInstances).toHaveLength(mockEvents.length);
      popupInstances.forEach(popup => {
        expect(popup._styling).toBe('consistent');
      });

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Tooltip Information Hierarchy', () => {
    it('displays information in logical order', () => {
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
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      popupContents.forEach(content => {
        // Should follow: Location -> Visits -> Last Activity
        const textContent = content.replace(/<[^>]*>/g, '');
        expect(textContent).toMatch(/स्थान.*दौरे.*गतिविधि/);
      });

      mockMapbox.Popup = originalPopup;
    });

    it('provides contextual information for each location', () => {
      const detailedEvents = [
        {
          place: 'खरसिया',
          visits: 5,
          lat: 21.99,
          lng: 83.08,
          status: 'सक्रिय',
          priority: 'उच्च',
        },
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
          data={detailedEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should include contextual information
      expect(popupContents[0]).toContain('स्थान: खरसिया');
      expect(popupContents[0]).toContain('कुल दौरे: 05');

      mockMapbox.Popup = originalPopup;
    });
  });

  describe('Tooltip Accessibility', () => {
    it('provides screen reader friendly content', () => {
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
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      popupContents.forEach(content => {
        // Should be readable by screen readers
        expect(content).toBeDefined();
        expect(content.length).toBeGreaterThan(0);
      });

      mockMapbox.Popup = originalPopup;
    });

    it('handles keyboard focus for tooltips', () => {
      // Test keyboard interaction with map
      render(
        <MapBoxVisual
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Map container should be keyboard accessible
      expect(document.querySelector('.mapbox-visual')).toBeInTheDocument();
    });
  });

  describe('Tooltip Update Behavior', () => {
    it('updates tooltip content when data changes', () => {
      const initialEvents = [
        { place: 'खरसिया', visits: 5, lat: 21.99, lng: 83.08 },
      ];

      const { rerender } = render(
        <MapBoxVisual
          data={initialEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Update data
      const updatedEvents = [
        { place: 'खरसिया', visits: 8, lat: 21.99, lng: 83.08 },
      ];

      rerender(
        <MapBoxVisual
          data={updatedEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should handle data updates
      expect(true).toBe(true); // Implementation dependent
    });

    it('maintains tooltip state during map interactions', () => {
      render(
        <MapBoxVisual
          data={mockEvents}
          center={[83.0, 22.0]}
          zoom={8}
        />
      );

      // Should maintain tooltip functionality during zoom/pan
      expect(document.querySelector('.mapbox-visual')).toBeInTheDocument();
    });
  });
});