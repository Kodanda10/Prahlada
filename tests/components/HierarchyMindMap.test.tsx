import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';
import { getHierarchyData } from '../../utils/testDataLoader';
import React from 'react';

describe('HierarchyMindMap', () => {
  const mockData = getHierarchyData();

  it('renders SVG element', () => {
    const { container } = render(<HierarchyMindMap data={mockData} />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('renders Hindi labels correctly', () => {
    const { getAllByText } = render(<HierarchyMindMap data={mockData} />);
    // Check for partial matches since labels contain counts like "रायगढ़ (142)"
    expect(getAllByText(/रायगढ़/)[0]).toBeInTheDocument();
    expect(getAllByText(/खरसिया/)[0]).toBeInTheDocument();
  });

  it('renders Legend in Hindi', () => {
    const { getByText } = render(<HierarchyMindMap data={mockData} />);
    expect(getByText('जिला')).toBeInTheDocument();
    expect(getByText('विधानसभा')).toBeInTheDocument();
    expect(getByText('ग्राम/वार्ड')).toBeInTheDocument();
  });
});
