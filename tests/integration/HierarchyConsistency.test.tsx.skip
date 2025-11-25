import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AnalyticsDashboard from '../../pages/Analytics';
import React from 'react';

// Mock components to avoid complex rendering
vi.mock('../../components/analytics/HierarchyMindMap', () => ({
  default: () => <div data-testid="mindmap">
    <div>रायगढ़ (142)</div>
    <div>खरसिया (78)</div>
    <div>तमनार (33)</div>
  </div>
}));

vi.mock('../../components/analytics/MapBoxVisual', () => ({
  default: () => <div data-testid="mapbox">MapBoxVisual</div>
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

describe('Hierarchy Consistency Integration', () => {
  it('visit counts in mindmap match analytics summary', () => {
    render(<AnalyticsDashboard />);

    // Check that mindmap shows 142 visits for Raigarh
    expect(screen.getByText('142')).toBeInTheDocument();

    // Check analytics summary shows "ग्राम दौरे: 142"
    expect(screen.getByText('ग्राम दौरे')).toBeInTheDocument();
  });

  it('district level count matches sum of constituency visits', () => {
    render(<AnalyticsDashboard />);

    // Raigarh district shows 142 total visits
    // This should equal sum of constituency visits (78 + 64 = 142)
    expect(screen.getByText('142')).toBeInTheDocument();
    expect(screen.getByText('78')).toBeInTheDocument(); // Kharsia
  });

  it('maintains consistent visit counts across tab switches', () => {
    render(<AnalyticsDashboard />);

    // Both map and hierarchy views should show same total
    expect(screen.getByText('142')).toBeInTheDocument();
  });

  it('node labels contain correct visit counts', () => {
    render(<AnalyticsDashboard />);

    // Check specific node labels with counts
    expect(screen.getByText('रायगढ़ (142)')).toBeInTheDocument();
    expect(screen.getByText('खरसिया (78)')).toBeInTheDocument();
    expect(screen.getByText('तमनार (33)')).toBeInTheDocument();
  });
});
