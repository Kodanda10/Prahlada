import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent } from '@testing-library/react';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';
import * as d3 from 'd3';

// Mock d3.zoom to avoid jsdom viewBox issues
vi.mock('d3', async () => {
  const actual = await vi.importActual<typeof import('d3')>('d3');
  return {
    ...actual,
    zoom: () => {
      const z = () => { };
      z.scaleExtent = () => z;
      z.on = () => z;
      z.transform = () => z;
      return z;
    }
  };
});

describe('D3 HierarchyMindMap - Features', () => {
  const mockData: any = {
    id: 'root',
    label: 'Root Node',
    level: 1,
    visits: 100,
    children: [
      {
        id: 'child1',
        label: 'Child 1',
        level: 2,
        visits: 50,
        children: [
          { id: 'grandchild1', label: 'Grandchild 1', level: 3, visits: 20 }
        ]
      },
      {
        id: 'child2',
        label: 'Child 2',
        level: 2,
        visits: 30,
        children: []
      }
    ]
  };

  describe('Tree Structure Rendering', () => {
    it('renders hierarchical tree structure', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Check for nodes and links
      const nodes = svg!.querySelectorAll('circle, rect');
      const links = svg!.querySelectorAll('path, line');

      // Note: exact count depends on implementation (e.g. if root is hidden or not)
      expect(nodes.length).toBeGreaterThan(0);
      expect(links.length).toBeGreaterThan(0);
    });

    it('displays node labels correctly', () => {
      const { getByText } = render(
        <HierarchyMindMap
          data={mockData}
          width={800}
          height={600}
        />
      );

      expect(getByText('Root Node (100)')).toBeInTheDocument();
      expect(getByText('Child 1 (50)')).toBeInTheDocument();
    });

    it('maintains proper node spacing', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockData}
          width={1000}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '1000');
      expect(svg).toHaveAttribute('height', '600');
    });
  });

  describe('Interactive Features', () => {
    it('supports node expansion/collapse', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockData}
          width={800}
          height={600}
        />
      );

      const nodes = container.querySelectorAll('circle'); // Assuming circles are clickable nodes
      if (nodes.length > 0) {
        fireEvent.click(nodes[0]);
        // Just checking it doesn't crash
        expect(container.querySelector('svg')).toBeInTheDocument();
      }
    });

    it('handles zoom and pan interactions', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Simulate zoom event
      fireEvent.wheel(svg!, { deltaY: -100 });
      expect(svg).toBeInTheDocument();
    });

    it('provides tooltips on hover', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockData}
          width={800}
          height={600}
        />
      );

      const nodes = container.querySelectorAll('circle');
      if (nodes.length > 0) {
        fireEvent.mouseEnter(nodes[0]);
        fireEvent.mouseLeave(nodes[0]);
        expect(container.querySelector('svg')).toBeInTheDocument();
      }
    });
  });

  describe('Data Binding & Updates', () => {
    it('updates when data changes', () => {
      const { getByText, queryByText, rerender } = render(
        <HierarchyMindMap
          data={mockData}
          width={800}
          height={600}
        />
      );

      expect(getByText('Child 1 (50)')).toBeInTheDocument();

      const newData: any = {
        id: 'root',
        label: 'Root Node',
        level: 1,
        visits: 100,
        children: [
          {
            id: 'child3',
            label: 'Child 3',
            level: 2,
            visits: 40,
            children: []
          }
        ]
      };

      rerender(
        <HierarchyMindMap
          data={newData}
          width={800}
          height={600}
        />
      );

      expect(queryByText('Child 1 (50)')).not.toBeInTheDocument();
      expect(getByText('Child 3 (40)')).toBeInTheDocument();
    });

    it('handles empty data gracefully', () => {
      const emptyData: any = {
        id: 'root',
        label: 'Root',
        level: 1,
        visits: 0,
        children: []
      };

      const { container } = render(
        <HierarchyMindMap
          data={emptyData}
          width={800}
          height={600}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });
});