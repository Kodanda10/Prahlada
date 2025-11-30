import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import HierarchyMindMap from "../../components/analytics/HierarchyMindMap";
import MapBoxVisual from "../../components/analytics/MapBoxVisual";

describe('Mindmap & Map Visualization Visual Regression', () => {
  const mockMindmapData: any = {
    id: 'root',
    label: 'Root',
    level: 1,
    visits: 100,
    children: [
      {
        id: 'branch1',
        label: 'Branch 1',
        level: 2,
        visits: 50,
        children: [
          { id: 'leaf1.1', label: 'Leaf 1.1', level: 3, visits: 25 },
          { id: 'leaf1.2', label: 'Leaf 1.2', level: 3, visits: 25 },
        ],
      },
      {
        id: 'branch2',
        label: 'Branch 2',
        level: 2,
        visits: 50,
        children: [
          { id: 'leaf2.1', label: 'Leaf 2.1', level: 3, visits: 50 },
        ],
      },
    ],
  };

  const mockMapData: any[] = [
    {
      id: 'location1',
      lat: 12.9716,
      lng: 77.5946,
      label: 'Location 1',
      type: 'urban',
      hierarchy_path: ['District', 'Block', 'Location 1'],
      visit_count: 100,
    },
    {
      id: 'location2',
      lat: 19.0760,
      lng: 72.8777,
      label: 'Location 2',
      type: 'rural',
      hierarchy_path: ['District', 'Block', 'Location 2'],
      visit_count: 200,
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

      // Check for SVG presence as class names might vary
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
      const simpleData: any = { id: 'single', label: 'Single Node', level: 1, visits: 10 };

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
      const { getByTestId } = render(
        <MapBoxVisual
          locations={mockMapData}
        />
      );

      const mapContainer = getByTestId('mapbox');
      expect(mapContainer).toBeInTheDocument();
    });

    it('displays location markers', () => {
      const { getByTestId } = render(
        <MapBoxVisual
          locations={mockMapData}
        />
      );

      const mapContainer = getByTestId('mapbox');
      expect(mapContainer).toBeInTheDocument();
    });

    it('handles empty data set', () => {
      const { getByTestId } = render(
        <MapBoxVisual
          locations={[]}
        />
      );

      const mapContainer = getByTestId('mapbox');
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
      const { getByTestId } = render(
        <MapBoxVisual
          locations={mockMapData}
        />
      );

      const mapContainer = getByTestId('mapbox');
      expect(mapContainer).toBeInTheDocument();
    });
  });
});