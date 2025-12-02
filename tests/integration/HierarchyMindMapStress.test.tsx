import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';
import React from 'react';

describe('HierarchyMindMapStress', () => {
  it('renders static nodes quickly', () => {
    const startTime = performance.now();
    render(<HierarchyMindMap />);
    const endTime = performance.now();
    expect(endTime - startTime).toBeLessThan(1000);
  });

  it('handles node count (10+ nodes)', () => {
    render(<HierarchyMindMap />);
    const nodes = screen.getAllByText(/\(.*\)/); // Labels with counts
    expect(nodes.length).toBeGreaterThan(10);
  });
});
