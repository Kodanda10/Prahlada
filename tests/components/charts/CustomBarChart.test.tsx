import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import CustomBarChart from '../../../components/charts/CustomBarChart';
import React from 'react';

describe('CustomBarChart', () => {
  it('renders the chart container', () => {
    const mockData = [
      { name: '?????', value: 10 },
      { name: '?????', value: 20 },
      { name: '?????', value: 30 }
    ];

    render(<CustomBarChart data={mockData} />);
    // Mocked recharts renders 'Bar Chart'
    expect(screen.getByText('Bar Chart')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    render(<CustomBarChart data={[]} />);
    expect(screen.getByText('Bar Chart')).toBeInTheDocument();
  });

  it('renders with extreme outliers', () => {
    const outlierData = [
      { name: '???????', value: 1 },
      { name: '??????', value: 100000 }
    ];
    render(<CustomBarChart data={outlierData} />);
    expect(screen.getByText('Bar Chart')).toBeInTheDocument();
  });
});
