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

  it('handles multiple markers (5 in current impl)', () => {
    render(<MapBoxVisual />);
    const markers = screen.getAllByTestId('icon-MapPin');
    expect(markers.length).toBe(6); // 5 markers + 1 legend
  });
});
