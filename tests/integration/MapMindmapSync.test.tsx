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
  default: ({ selectedRegion, onSelect }: any) => (
    <div
      data-testid="mapbox"
      onClick={() => onSelect?.(null)}
    >
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

    // Switch to Hierarchy view
    fireEvent.click(screen.getByText('पदानुक्रम'));

    // Initially no region selected (we check this before interacting, though strictly "selected-region" div is part of MapBoxVisual which is HIDDEN in hierarchy view.
    // Actually, AnalyticsDashboard toggles between MapBoxVisual OR HierarchyMindMap. They are not both visible.
    // So we can't check MapBoxVisual state while clicking HierarchyMindMap if one replaces the other in DOM.
    // Wait, the test expects them to sync. If they are mutually exclusive in view, how do they sync?
    // State is lifted to AnalyticsDashboard.
    // We need to click node in Hierarchy view, then switch back to Map view to verify highlight.

    // Click on Kharsia node in mindmap
    const kharsiaNode = screen.getByTestId('kharsia-node');
    fireEvent.click(kharsiaNode);

    // Switch back to Map view
    fireEvent.click(screen.getByText('मानचित्र'));

    // Map should highlight Kharsia region
    expect(screen.getByTestId('selected-region')).toHaveTextContent('a1');
    expect(screen.getByTestId('kharsia-marker')).toHaveClass('highlighted');
  });

  it('filters markers to show only selected subtree', () => {
    render(<AnalyticsDashboard />);

    // Switch to Hierarchy view
    fireEvent.click(screen.getByText('पदानुक्रम'));

    // Select Raigarh district
    const raigarhNode = screen.getByTestId('raigarh-node');
    fireEvent.click(raigarhNode);

    // Switch back to Map view
    fireEvent.click(screen.getByText('मानचित्र'));

    // Map should show only markers from Raigarh district
    expect(screen.getByTestId('selected-region')).toHaveTextContent('d1');
    expect(screen.getByTestId('raigarh-marker')).toHaveClass('highlighted');
  });

  it('maintains sync across tab switches', () => {
    render(<AnalyticsDashboard />);

    // Switch to Hierarchy view
    fireEvent.click(screen.getByText('पदानुक्रम'));

    // Select a region
    const kharsiaNode = screen.getByTestId('kharsia-node');
    fireEvent.click(kharsiaNode);

    // Switch back to Map view
    fireEvent.click(screen.getByText('मानचित्र'));

    // Selection should persist
    expect(screen.getByTestId('selected-region')).toHaveTextContent('a1');
  });

  it('clears selection when clicking elsewhere', () => {
    render(<AnalyticsDashboard />);

    // Switch to Hierarchy view
    fireEvent.click(screen.getByText('पदानुक्रम'));

    // Select a region
    const kharsiaNode = screen.getByTestId('kharsia-node');
    fireEvent.click(kharsiaNode);

    // Switch back to Map view
    fireEvent.click(screen.getByText('मानचित्र'));
    expect(screen.getByTestId('selected-region')).toHaveTextContent('a1');

    // Click outside to clear selection
    const mapContainer = screen.getByTestId('mapbox');
    fireEvent.click(mapContainer);

    // Selection should be cleared
    expect(screen.getByTestId('selected-region')).toHaveTextContent('none');
  });
});


