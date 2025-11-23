import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import MapBoxVisual from '../../components/analytics/MapBoxVisual';
import React from 'react';

describe('MapBoxVisual Rendering', () => {
  it('renders the map container', () => {
    const { container } = render(<MapBoxVisual />);
    expect(container.firstChild).toHaveClass('relative', 'w-full', 'bg-[#0f172a]');
  });

  it('renders specific markers with Hindi labels', () => {
    render(<MapBoxVisual />);
    expect(screen.getByText(/??????/)).toBeInTheDocument();
    expect(screen.getByText(/?????? ???/)).toBeInTheDocument();
    expect(screen.getByText(/???????/)).toBeInTheDocument();
  });

  it('renders the legend', () => {
    render(<MapBoxVisual />);
    expect(screen.getByText(/?????? ???? ?????/)).toBeInTheDocument();
  });

  it('renders marker pins', () => {
    render(<MapBoxVisual />);
    // We use lucide-react mock which adds data-testid="icon-MapPin"
    const pins = screen.getAllByTestId('icon-MapPin');
    expect(pins.length).toBeGreaterThanOrEqual(5); // 5 markers + 1 legend
  });
});
