import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import CustomPieChart from '../../../components/charts/CustomPieChart';
import React from 'react';

describe('CustomPieChart', () => {
  it('renders the chart container', () => {
    // Mock props for the chart
    const mockData = [
      { name: '??????', value: 30, fill: '#8884d8' },
      { name: '???????', value: 25, fill: '#82ca9d' },
      { name: '??????', value: 45, fill: '#ffc658' }
    ];

    render(<CustomPieChart data={mockData} />);
    // Since we mocked recharts in setup.ts, it renders 'Pie Chart'
    expect(screen.getByText('Pie Chart')).toBeInTheDocument();
  });

  it('renders with empty data gracefully', () => {
    render(<CustomPieChart data={[]} />);
    expect(screen.getByText('Pie Chart')).toBeInTheDocument();
  });

  it('renders with sparse data', () => {
    const sparseData = [{ name: '??', value: 1, fill: '#8884d8' }];
    render(<CustomPieChart data={sparseData} />);
    expect(screen.getByText('Pie Chart')).toBeInTheDocument();
  });
});
