
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HierarchyMindMap from '../components/analytics/HierarchyMindMap';

describe('HierarchyMindMap', () => {
  it('renders SVG element', () => {
    const { container } = render(<HierarchyMindMap />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('renders Hindi labels correctly', () => {
    const { getByText } = render(<HierarchyMindMap />);
    // Check for partial matches since labels contain counts like "रायगढ़ (142)"
    expect(getByText(/रायगढ़/)).toBeInTheDocument();
    expect(getByText(/खरसिया/)).toBeInTheDocument();
  });

  it('renders Legend in Hindi', () => {
    const { getByText } = render(<HierarchyMindMap />);
    expect(getByText('जिला')).toBeInTheDocument();
    expect(getByText('विधानसभा')).toBeInTheDocument();
    expect(getByText('ग्राम/वार्ड')).toBeInTheDocument();
  });
});
