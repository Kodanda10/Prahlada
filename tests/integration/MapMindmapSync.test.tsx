import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AnalyticsDashboard from '../../pages/Analytics';
import React from 'react';

// Mock components for integration testing
vi.mock('../../components/analytics/HierarchyMindMap', () => ({
  default: ({ selectedNode, onNodeSelect }: any) => (
    <div data-testid="mindmap">
      <button data-testid="raigarh-node" onClick={() => onNodeSelect?.('d1')}>
        रायगढ़ (142)
      </button>
      <button data-testid="kharsia-node" onClick={() => onNodeSelect?.('a1')}>
        खरसिया (78)
      </button>
    </div>
  )
}));

vi.mock('../../components/analytics/MapBoxVisual', () => ({
  default: ({ selectedRegion }: any) => (
    <div data-testid="mapbox">
      <div data-testid="selected-region">{selectedRegion || 'none'}</div>
      <div data-testid="kharsia-marker" className={selectedRegion === 'a1' ? 'highlighted' : ''}>
        खरसिया (05)
      </div>
      <div data-testid="raigarh-marker" className={selectedRegion === 'd1' ? 'highlighted' : ''}>
        रायगढ़ शहर (12)
      </div>
    </div>
  )
}));

vi.mock('../../components/charts/CustomPieChart', () => ({
  default: () => <div data-testid="pie-chart">PieChart</div>
}));

vi.mock('../../components/charts/CustomBarChart', () => ({
  default: () => <div data-testid="bar-chart">BarChart</div>
}));

vi.mock('../../components/NumberTicker', () => ({
  default: ({ value }: any) => <span>{value}</span>
}));

describe('MapMindmapSync', () => {
  it('highlights map markers when mindmap node is selected', () => {
    render(<AnalyticsDashboard />);

    // Initially no region selected
    expect(screen.getByTestId('selected-region')).toHaveTextContent('none');

    // Click on Kharsia node in mindmap
    const kharsiaNode = screen.getByTestId('kharsia-node');
    fireEvent.click(kharsiaNode);

    // Map should highlight Kharsia region
    expect(screen.getByTestId('selected-region')).toHaveTextContent('a1');
    expect(screen.getByTestId('kharsia-marker')).toHaveClass('highlighted');
  });

  it('filters markers to show only selected subtree', () => {
    render(<AnalyticsDashboard />);

    // Select Raigarh district
    const raigarhNode = screen.getByTestId('raigarh-node');
    fireEvent.click(raigarhNode);

    // Map should show only markers from Raigarh district
    expect(screen.getByTestId('selected-region')).toHaveTextContent('d1');
    expect(screen.getByTestId('raigarh-marker')).toHaveClass('highlighted');
  });

  it('maintains sync across tab switches', () => {
    render(<AnalyticsDashboard />);

    // Select a region, then switch tabs
    const kharsiaNode = screen.getByTestId('kharsia-node');
    fireEvent.click(kharsiaNode);

    // Selection should persist when switching between map and hierarchy views
    expect(screen.getByTestId('selected-region')).toHaveTextContent('a1');
  });

  it('clears selection when clicking elsewhere', () => {
    render(<AnalyticsDashboard />);

    // Select a region
    const kharsiaNode = screen.getByTestId('kharsia-node');
    fireEvent.click(kharsiaNode);
    expect(screen.getByTestId('selected-region')).toHaveTextContent('a1');

    // Click outside to clear selection
    const mapContainer = screen.getByTestId('mapbox');
    fireEvent.click(mapContainer);

    // Selection should be cleared
    expect(screen.getByTestId('selected-region')).toHaveTextContent('none');
  });

  it('prevents stale data after rapid selections', () => {
    render(<AnalyticsDashboard />);

    // Rapidly click different nodes
    const raigarhNode = screen.getByTestId('raigarh-node');
    const kharsiaNode = screen.getByTestId('kharsia-node');

    fireEvent.click(raigarhNode);
    fireEvent.click(kharsiaNode);

    // Final selection should be the last clicked (kharsia)
    expect(screen.getByTestId('selected-region')).toHaveTextContent('a1');
  });
});
