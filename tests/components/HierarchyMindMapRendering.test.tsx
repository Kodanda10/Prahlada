import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';
import React from 'react';

describe('HierarchyMindMap Rendering', () => {
  it('renders the container correctly', () => {
    const { container } = render(<HierarchyMindMap />);
    expect(container.firstChild).toHaveClass('relative', 'w-full', 'h-full');
  });

  it('renders the root node (District)', () => {
    render(<HierarchyMindMap />);
    // Regex to match "रायगढ़ (142)" or similar
    expect(screen.getAllByText(/रायगढ़/).length).toBeGreaterThan(0);
  });

  it('renders secondary nodes (Assembly)', () => {
    render(<HierarchyMindMap />);
    // Use getAllByText because some text might appear in labels and tooltips/legend
    expect(screen.getAllByText(/खरसिया/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/रायगढ़ शहर/).length).toBeGreaterThan(0);
  });

  it('renders leaf nodes (Villages/Wards)', () => {
    render(<HierarchyMindMap />);
    expect(screen.getByText(/ग्राम जोबी/)).toBeInTheDocument();
    expect(screen.getByText(/वार्ड 04/)).toBeInTheDocument();
  });

  it('displays the legend with correct Hindi labels', () => {
    render(<HierarchyMindMap />);
    expect(screen.getByText('जिला')).toBeInTheDocument();
    expect(screen.getByText('विधानसभा')).toBeInTheDocument();
    expect(screen.getByText('विकासखंड')).toBeInTheDocument();
    expect(screen.getByText('पंचायत/जोन')).toBeInTheDocument();
    expect(screen.getByText('ग्राम/वार्ड')).toBeInTheDocument();
  });

  it('renders connections between nodes', () => {
    const { container } = render(<HierarchyMindMap />);
    const paths = container.querySelectorAll('line'); // D3 uses 'line' for links in this component
    expect(paths.length).toBeGreaterThan(0);
  });
});
