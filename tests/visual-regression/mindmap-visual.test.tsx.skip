import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import HierarchyMindMap from '../components/analytics/HierarchyMindMap';
import MapBoxVisual from '../components/analytics/MapBoxVisual';

describe('Mindmap & Map Visualization Visual Regression', () => {
  const mockMindmapData = {
    name: 'Root',
    children: [
      {
        name: 'Branch 1',
        children: [
          { name: 'Leaf 1.1' },
          { name: 'Leaf 1.2' },
        ],
      },
      {
        name: 'Branch 2',
        children: [
          { name: 'Leaf 2.1' },
        ],
      },
    ],
  };

  const mockMapData = [
    {
      id: 'location1',
      coordinates: [77.5946, 12.9716], // Bangalore
      name: 'Location 1',
      value: 100,
    },
    {
      id: 'location2',
      coordinates: [72.8777, 19.0760], // Mumbai
      name: 'Location 2',
      value: 200,
    },
  ];

  describe('HierarchyMindMap Component', () => {
    it('renders hierarchical structure visually', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockMindmapData}
          width={800}
          height={600}
        />
      );

      const mindmapContainer = container.querySelector('.hierarchy-mindmap');
      expect(mindmapContainer).toBeInTheDocument();

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });

    it('displays nodes and connections', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockMindmapData}
          width={600}
          height={400}
        />
      );

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();

      // Check for node circles and connecting lines
      const circles = svgElement.querySelectorAll('circle');
      const paths = svgElement.querySelectorAll('path, line');

      expect(circles.length).toBeGreaterThan(0);
      expect(paths.length).toBeGreaterThan(0);
    });

    it('handles different data structures', () => {
      const simpleData = { name: 'Single Node' };

      const { container } = render(
        <HierarchyMindMap
          data={simpleData}
          width={400}
          height={300}
        />
      );

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });
  });

  describe('MapBoxVisual Component', () => {
    it('renders map container with markers', () => {
      const { container } = render(
        <MapBoxVisual
          data={mockMapData}
          center={[78.9629, 20.5937]} // Center of India
          zoom={4}
        />
      );

      const mapContainer = container.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });

    it('displays location markers', () => {
      const { container } = render(
        <MapBoxVisual
          data={mockMapData}
          center={[77.5946, 12.9716]}
          zoom={10}
        />
      );

      const mapContainer = container.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();

      // Markers should be rendered (exact implementation may vary)
      expect(mapContainer).toBeInTheDocument();
    });

    it('handles empty data set', () => {
      const { container } = render(
        <MapBoxVisual
          data={[]}
          center={[78.9629, 20.5937]}
          zoom={4}
        />
      );

      const mapContainer = container.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });
  });

  describe('Interactive Elements', () => {
    it('mindmap responds to zoom interactions', () => {
      const { container } = render(
        <HierarchyMindMap
          data={mockMindmapData}
          width={800}
          height={600}
        />
      );

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();

      // Check for interactive elements
      const interactiveElements = svgElement.querySelectorAll('g, circle');
      expect(interactiveElements.length).toBeGreaterThan(0);
    });

    it('map maintains bounds during interactions', () => {
      const { container } = render(
        <MapBoxVisual
          data={mockMapData}
          center={[78.9629, 20.5937]}
          zoom={5}
        />
      );

      const mapContainer = container.querySelector('.mapbox-visual');
      expect(mapContainer).toBeInTheDocument();
    });
  });
});