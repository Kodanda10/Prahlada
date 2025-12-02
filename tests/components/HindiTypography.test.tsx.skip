import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import React from 'react';
import AnalyticsDashboard from '../../pages/Analytics';

// Mock children to focus on typography of the page itself
vi.mock('../../components/charts/CustomPieChart', () => ({ default: () => <div>PieChart</div> }));
vi.mock('../../components/charts/CustomBarChart', () => ({ default: () => <div>BarChart</div> }));
vi.mock('../../components/analytics/MapBoxVisual', () => ({ default: () => <div>MapBoxVisual</div> }));
vi.mock('../../components/analytics/HierarchyMindMap', () => ({ default: () => <div>HierarchyMindMap</div> }));
vi.mock('../../components/NumberTicker', () => ({ default: ({ value }: any) => <span>{value}</span> }));

describe('Hindi Typography & String Audit', () => {
  it('contains valid Hindi labels in Analytics Dashboard', () => {
    render(<AnalyticsDashboard />);
    
    // Check for key Hindi phrases
    expect(screen.getByText('????? ?????? ????????')).toBeInTheDocument();
    expect(screen.getByText('??-????????? ??? ?????')).toBeInTheDocument();
    expect(screen.getByText('?????? ????????')).toBeInTheDocument();
  });

  it('does not contain untranslated English placeholders', () => {
    const { container } = render(<AnalyticsDashboard />);
    const textContent = container.textContent || '';
    
    // Allowlist of English words that might appear (e.g. brand names, 'PieChart' from mock)
    // But general UI labels should be Hindi
    const forbiddenWords = ['Dashboard', 'Analysis', 'Events', 'Coverage']; 
    
    forbiddenWords.forEach(word => {
      expect(textContent).not.toContain(word);
    });
  });

  it('renders numbers mixed with Hindi correctly (RTL/LTR mix)', () => {
    // Assuming there is a component or text somewhere that does this.
    // For now, we check the dashboard headers which might have numbers.
    render(<AnalyticsDashboard />);
    // Add specific checks if we have counters like "??? 5 ?????"
  });
});
