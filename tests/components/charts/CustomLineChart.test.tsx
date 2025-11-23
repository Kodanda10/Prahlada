import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import CustomLineChart from '../../../components/charts/CustomLineChart';
import React from 'react';

describe('CustomLineChart', () => {
  it('renders the chart container', () => {
    const mockData = [
      { name: '??? 1', value: 10 },
      { name: '??? 2', value: 20 },
      { name: '??? 3', value: 30 }
    ];

    render(<CustomLineChart data={mockData} />);
    expect(screen.getByText('Line Chart')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    render(<CustomLineChart data={[]} />);
    expect(screen.getByText('Line Chart')).toBeInTheDocument();
  });
});
