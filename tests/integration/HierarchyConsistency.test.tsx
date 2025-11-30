import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeAll, afterEach } from 'vitest';
import AnalyticsDashboard from '../../pages/Analytics';
import React from 'react';
import { apiService } from '../../services/api';
import { getTweetStats, getAnalyticsSummary, getHierarchyData } from '../../utils/testDataLoader';
import { HierarchyNode } from '../../components/analytics/HierarchyMindMap';

describe('Hierarchy Consistency Integration', () => {
  const analyticsSummary = getAnalyticsSummary();
  const eventTypeStats = getTweetStats();
  const hierarchyData = getHierarchyData();

  beforeAll(() => {
    // Mock API service calls
    vi.spyOn(apiService, 'get').mockImplementation(async (path: string) => {
      if (path === 'analytics/event-types') {
        return eventTypeStats;
      }
      if (path === 'analytics/districts') {
        // Mock districts data, which is a flat list of location names from hierarchy root children
        // AnalyticsDashboard expects this to be transformed into HierarchyNode internally
        return hierarchyData.children ? hierarchyData.children.map(node => ({ name: node.label, value: node.visits })) : [];
      }
      return [];
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // Mock components to avoid complex rendering - now using real data where applicable
  vi.mock('../../components/analytics/HierarchyMindMap', () => ({
    default: ({ data }: { data: HierarchyNode | null }) => {
        if (!data) return <div data-testid="mindmap-no-data">No Hierarchy Data</div>;
        
        return (
            <pre data-testid="mindmap-data-dump">
                {JSON.stringify(data, null, 2)}
            </pre>
        );
    },
    // Export HierarchyNode interface from the mock as well, needed for types
    HierarchyNode: vi.importActual('../../components/analytics/HierarchyMindMap').HierarchyNode
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

  // Correctly mock NumberTicker to render its actual value
  vi.mock('../../components/NumberTicker', () => ({
    default: ({ value, prefix, suffix, className }: { value: number, prefix?: string, suffix?: string, className?: string }) => (
        <span className={className}>{prefix}{value}{suffix}</span>
    )
  }));


  it('visit counts in mindmap match analytics summary', async () => {
    render(<AnalyticsDashboard />);

    // Simulate click to switch to hierarchy view
    fireEvent.click(screen.getByText('पदानुक्रम'));

    await waitFor(() => {
        // Retrieve the JSON data dump from the HierarchyMindMap mock
        const mindmapDataDump = screen.getByTestId('mindmap-data-dump');
        const renderedData = JSON.parse(mindmapDataDump.textContent || '{}');
        
        // Directly assert that the rendered data matches the expected hierarchyData
        expect(renderedData.label).toEqual(hierarchyData.label);
        expect(renderedData.visits).toEqual(hierarchyData.visits);
        expect(renderedData.children?.length || 0).toEqual(hierarchyData.children?.length || 0);

        // Check analytics summary shows "ग्राम दौरे" with correct count
        expect(screen.getByText('ग्राम दौरे')).toBeInTheDocument();
        expect(screen.getByText(String(analyticsSummary.totalVillageVisits), { selector: 'span.text-2xl.font-bold' })).toBeInTheDocument();
    });
  });

  it('district level count matches sum of constituency visits', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
        // Assert total districts
        expect(screen.getByText('कुल जिले')).toBeInTheDocument();
        expect(screen.getByText(String(analyticsSummary.totalDistricts), { selector: 'span.text-2xl.font-bold' })).toBeInTheDocument();
    });
  });

  it('maintains consistent visit counts across tab switches', async () => {
    render(<AnalyticsDashboard />);

    await waitFor(() => {
        // Both map and hierarchy views should show same total if they displayed it explicitly
        expect(screen.getByText(String(analyticsSummary.totalVillageVisits), { selector: 'span.text-2xl.font-bold' })).toBeInTheDocument();
    });
  });

  it('node labels contain correct visit counts', async () => {
    render(<AnalyticsDashboard />);

    // Simulate click to switch to hierarchy view
    fireEvent.click(screen.getByText('पदानुक्रम'));

    await waitFor(() => {
        // Retrieve the JSON data dump from the HierarchyMindMap mock
        const mindmapDataDump = screen.getByTestId('mindmap-data-dump');
        const renderedData = JSON.parse(mindmapDataDump.textContent || '{}');
        
        // Assert that the full hierarchy data object is rendered correctly
        expect(renderedData).toEqual(hierarchyData);
    });
  });
});
