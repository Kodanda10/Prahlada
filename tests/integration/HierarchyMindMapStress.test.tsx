import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';
import React from 'react';

describe('HierarchyMindMapStress', () => {
  it('renders static nodes quickly', () => {
    const startTime = performance.now();
    render(<HierarchyMindMap data={mockData} />);
    const endTime = performance.now();
    expect(endTime - startTime).toBeLessThan(1000);
  });

  const mockData: any = {
    id: 'root',
    label: 'Root',
    level: 1,
    visits: 100,
    children: Array.from({ length: 15 }, (_, i) => ({
      id: `child-${i}`,
      label: `Child ${i} (5)`,
      level: 2,
      visits: 10,
      children: []
    }))
  };

  it('handles node count (10+ nodes)', () => {
    render(<HierarchyMindMap data={mockData} />);
    const nodes = screen.getAllByText(/\(.*\)/); // Labels with counts
    expect(nodes.length).toBeGreaterThan(10);
  });
});
