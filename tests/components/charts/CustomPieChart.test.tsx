import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import CustomPieChart from '../../../components/charts/CustomPieChart';
import React from 'react';
import { getTweetStats } from '../../../utils/testDataLoader';

describe('CustomPieChart', () => {
  it('renders the chart container', () => {
    // Use real stats from tweets
    const realData = getTweetStats();
    // Take top 5 for chart
    const chartData = realData.slice(0, 5);

    render(<CustomPieChart data={chartData} />);
    // Since we mocked recharts in setup.ts, it renders 'Pie Chart'
    expect(screen.getByText('Pie Chart')).toBeInTheDocument();
  });

  it('renders with empty data gracefully', () => {
    render(<CustomPieChart data={[]} />);
    expect(screen.getByText('Pie Chart')).toBeInTheDocument();
  });

  it('renders with sparse data', () => {
    const realData = getTweetStats();
    // Use just one item if available
    const sparseData = realData.length > 0 ? [realData[0]] : [];
    render(<CustomPieChart data={sparseData} />);
    expect(screen.getByText('Pie Chart')).toBeInTheDocument();
  });
});
