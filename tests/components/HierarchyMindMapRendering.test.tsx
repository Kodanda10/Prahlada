import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HierarchyMindMap from '../../components/analytics/HierarchyMindMap';
import React from 'react';

describe('HierarchyMindMap Rendering', () => {
  it('renders the container correctly', () => {
    const { container } = render(<HierarchyMindMap />);
    expect(container.firstChild).toHaveClass('w-full', 'h-full', 'bg-[#0f172a]');
  });

  it('renders the root node (District)', () => {
    render(<HierarchyMindMap />);
    expect(screen.getByText(/??????/)).toBeInTheDocument();
  });

  it('renders secondary nodes (Assembly)', () => {
    render(<HierarchyMindMap />);
    expect(screen.getByText(/??????/)).toBeInTheDocument();
    expect(screen.getByText(/?????? ???/)).toBeInTheDocument();
  });

  it('renders leaf nodes (Villages/Wards)', () => {
    render(<HierarchyMindMap />);
    expect(screen.getByText(/????? ????/)).toBeInTheDocument();
    expect(screen.getByText(/????? 04/)).toBeInTheDocument();
  });

  it('displays the legend with correct Hindi labels', () => {
    render(<HierarchyMindMap />);
    expect(screen.getByText('????')).toBeInTheDocument();
    expect(screen.getByText('????????')).toBeInTheDocument();
    expect(screen.getByText('????????')).toBeInTheDocument();
    expect(screen.getByText('??????/???')).toBeInTheDocument();
    expect(screen.getByText('?????/?????')).toBeInTheDocument();
  });

  it('renders connections between nodes', () => {
    const { container } = render(<HierarchyMindMap />);
    const paths = container.querySelectorAll('path');
    expect(paths.length).toBeGreaterThan(0);
  });
});
