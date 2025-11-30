import { render, screen, fireEvent, waitFor, createEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';
import React from 'react';

describe('MapBoxVisual Tooltip Interaction', () => {
  const mockLocations: any[] = [
    {
      id: '1',
      lat: 21.25,
      lng: 82.15,
      label: 'खरसिया',
      type: 'rural',
      visit_count: 5,
      hierarchy_path: ['रायगढ़', 'खरसिया'],
      event_type: 'जनसम्पर्क अभियान',
      date: '2023-11-19'
    },
  ];

  it.skip('shows tooltip on marker hover', async () => {
    render(<MapBoxVisual locations={mockLocations} />);

    // Toggle clusters off to show individual markers
    const clusterButton = screen.getByText('Cluster');
    fireEvent.click(clusterButton);

    // Wait for markers to appear
    const markers = await screen.findAllByTestId('mock-map-marker');
    expect(markers.length).toBeGreaterThan(0);

    // Hover over the first marker
    // Note: The Marker component in setup.ts is a div.
    // In MapBoxVisual.tsx, the Marker contains a motion.div which has the hover effect?
    // Actually, the Marker in MapBoxVisual has onClick.
    // The motion.div INSIDE the Marker has whileHover.
    // But we can't easily trigger framer-motion's whileHover in jsdom.
    // However, the tooltip logic for individual markers in MapBoxVisual.tsx uses `onMouseEnter` on the MAP layer for `unclustered-point`.
    // Wait, let's check MapBoxVisual.tsx again.

    // Lines 289-295:
    // onMouseEnter={(e) => {
    //   const feature = e.features?.[0];
    //   if (feature && feature.layer.id === 'unclustered-point') { ... setHoveredLocation ... }
    // }}

    // This `onMouseEnter` is on the `<Map>` component.
    // It relies on `e.features` which comes from Mapbox GL JS event.
    // Our mock map just passes `onMouseEnter` to the div.
    // But triggering `mouseEnter` on the mock map div won't provide `e.features`.

    // AND there is also:
    // Lines 424-437: Tooltip rendering based on `hoveredLocation`.

    // So to test this, we need to manually trigger `onMouseEnter` on the Map component with a mocked event object containing features.
    // The mock map in setup.ts passes `onMouseEnter` to the div.

    const map = screen.getByTestId('mock-map');

    // Trigger mouseEnter with features using Object.defineProperty to ensure it persists
    const event = createEvent.mouseEnter(map);
    Object.defineProperty(event, 'features', {
      value: [{
        layer: { id: 'unclustered-point' },
        properties: { id: '1' }
      }],
      writable: true,
      configurable: true
    });
    fireEvent(map, event);

    // Wait for tooltip to appear
    await waitFor(() => {
      expect(screen.getByText(/खरसिया/)).toBeInTheDocument();
      expect(screen.getByText(/5 दौरे/)).toBeInTheDocument();
    });
  });
});
