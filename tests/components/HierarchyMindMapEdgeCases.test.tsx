import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HierarchyMindMap, { HierarchyNode } from '../../components/analytics/HierarchyMindMap';
import React from 'react';

describe('HierarchyMindMap Edge Cases', () => {
  const mockDistrictData: HierarchyNode = {
    id: 'district-1',
    label: 'रायगढ़',
    level: 1,
    visits: 100,
    children: [
      {
        id: 'block-1',
        label: 'खरसिया',
        level: 3,
        visits: 50,
        children: []
      }
    ]
  };

  const mockULBData: HierarchyNode = {
    id: 'district-1',
    label: 'रायगढ़',
    level: 1,
    visits: 100,
    children: [
      {
        id: 'ulb-1',
        label: 'रायगढ़ नगर निगम',
        level: 2,
        visits: 80,
        children: [
          {
            id: 'zone-1',
            label: 'जोन 1',
            level: 4,
            visits: 30,
            children: []
          }
        ]
      }
    ]
  };

  it('handles missing hierarchy levels gracefully', () => {
    render(<HierarchyMindMap data={mockDistrictData} />);

    // Should show all expected nodes
    expect(screen.getByText(/रायगढ़/)).toBeInTheDocument();
    expect(screen.getByText(/खरसिया/)).toBeInTheDocument();
  });

  it('shows notice for empty data', () => {
    render(<HierarchyMindMap data={null} />);
    expect(screen.getByText('कोई पदानुक्रम डेटा उपलब्ध नहीं है।')).toBeInTheDocument();
  });

  it('maintains layout integrity with edge case data', () => {
    const { container } = render(<HierarchyMindMap data={mockDistrictData} />);

    // Check that SVG structure is intact
    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();

    // Check that connections exist (lines)
    const lines = container.querySelectorAll('line');
    expect(lines.length).toBeGreaterThan(0);

    // Check that nodes are positioned (circles)
    const nodes = container.querySelectorAll('circle');
    expect(nodes.length).toBeGreaterThan(1); // At least root and one child
  });

  it('handles ULB mode hierarchies', () => {
    // Test for Urban Local Body mode (जिला → नगर निगम → ज़ोन → वार्ड)
    render(<HierarchyMindMap data={mockULBData} />);

    // Check it renders ULB specific labels
    expect(screen.getByText(/नगर निगम/)).toBeInTheDocument();
    expect(screen.getByText(/जोन 1/)).toBeInTheDocument();
  });
});
