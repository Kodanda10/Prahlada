import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';
import React from 'react';

describe('MapBoxVisualStress', () => {
  it('renders with static markers without lag', () => {
    const startTime = performance.now();
    render(<MapBoxVisual />);
    const endTime = performance.now();
    expect(endTime - startTime).toBeLessThan(1000);
  });

  it('handles multiple markers (5 in current impl)', async () => {
    const testData = Array.from({ length: 5 }, (_, i) => ({
      id: `loc-${i}`,
      lat: 21.25 + i * 0.01,
      lng: 82.15 + i * 0.01,
      label: `Location ${i}`,
      type: 'rural' as const,
      hierarchy_path: ['District', 'Block'],
      visit_count: 10
    }));

    const { getByText, getAllByTestId } = render(<MapBoxVisual locations={testData} />);
    
    // Toggle cluster to show markers
    const clusterBtn = getByText('Cluster');
    // We need to wait for initial load timeout in component (1500ms)? 
    // No, the map renders immediately but loading overlay is there.
    // The markers depend on mapLoaded. MockMap triggers onLoad immediately via useEffect.
    
    // However, the component has:
    // onClick={() => setShowClusters(!showClusters)}
    // It defaults to true. We click to make it false.
    const React = require('react');
    const { fireEvent } = require('@testing-library/react');
    fireEvent.click(clusterBtn);

    const markers = getAllByTestId('icon-MapPin');
    expect(markers.length).toBe(6); // 5 markers + 1 legend
  });
});
