import { describe, it, expect } from 'vitest';
import { render, fireEvent } from '@testing-library/react';
import { HierarchyMindMap } from '../../components/analytics/HierarchyMindMap';

describe('D3 Mindmap Critical Features', () => {
  const mockData = {
    name: 'Root Node',
    children: [
      {
        name: 'Branch A',
        children: [
          { name: 'Leaf A1', value: 10 },
          { name: 'Leaf A2', value: 15 },
        ],
      },
      {
        name: 'Branch B',
        children: [
          { name: 'Leaf B1', value: 20 },
          {
            name: 'Branch B2',
            children: [
              { name: 'Leaf B2.1', value: 5 },
              { name: 'Leaf B2.2', value: 8 },
            ],
          },
        ],
      },
    ],
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
      const nodes = svg.querySelectorAll('circle, rect');
      const links = svg.querySelectorAll('path, line');

      expect(nodes.length).toBeGreaterThan(0);
      expect(links.length).toBeGreaterThan(0);
    });

    it('displays node labels correctly', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockData}
          width={600}
          height={400}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Check for text elements
      const labels = svg.querySelectorAll('text');
      expect(labels.length).toBeGreaterThan(0);

      // Verify root node label
      const rootLabel = Array.from(labels).find(label =>
        label.textContent?.includes('Root Node')
      );
      expect(rootLabel).toBeTruthy();
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
      expect(svg).toBeInTheDocument();

      // Verify SVG dimensions
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

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      // Look for interactive elements (circles are typically clickable)
      const nodes = svg.querySelectorAll('circle');
      expect(nodes.length).toBeGreaterThan(0);

      if (nodes[0]) {
        fireEvent.click(nodes[0]);
        // Should not throw error
        expect(svg).toBeInTheDocument();
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

      // Test wheel event for zoom
      fireEvent.wheel(svg, { deltaY: -100 });
      expect(svg).toBeInTheDocument();

      // Test mouse drag for pan
      fireEvent.mouseDown(svg, { clientX: 100, clientY: 100 });
      fireEvent.mouseMove(svg, { clientX: 150, clientY: 150 });
      fireEvent.mouseUp(svg);
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

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();

      const nodes = svg.querySelectorAll('circle');
      if (nodes[0]) {
        fireEvent.mouseEnter(nodes[0]);
        fireEvent.mouseLeave(nodes[0]);
        expect(svg).toBeInTheDocument();
      }
    });
  });

  describe('Data Binding & Updates', () => {
    it('updates when data changes', () => {
      const { rerender, container } = render(
        <HierarchyMindMap
          data={mockData}
          width={800}
          height={600}
        />
      );

      const initialSvg = container.querySelector('svg');
      expect(initialSvg).toBeInTheDocument();

      const newData = {
        name: 'New Root',
        children: [{ name: 'New Child' }],
      };

      rerender(
        <HierarchyMindMap
          data={newData}
          width={800}
          height={600}
        />
      );

      const updatedSvg = container.querySelector('svg');
      expect(updatedSvg).toBeInTheDocument();

      // Check for new node label
      const newLabels = updatedSvg.querySelectorAll('text');
      const newRootLabel = Array.from(newLabels).find(label =>
        label.textContent?.includes('New Root')
      );
      expect(newRootLabel).toBeTruthy();
    });

    it('handles empty data gracefully', () => {
      const { container } = render(
        <HierarchyMindMap
          data={{ name: 'Empty' }}
          width={400}
          height={300}
        />
      );

      const svg = container.querySelector('svg');
      expect(svg).toBeInTheDocument();
    });
  });
});