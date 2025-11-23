import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import RiveLikeIcons from '../../components/interactions/RiveLikeIcons';
import React from 'react';

describe('RiveLikeIcons', () => {
  it('renders the component', () => {
    render(<RiveLikeIcons />);
    // Assuming it has some content or structure
    const container = screen.getByRole('generic'); // Basic check
    expect(container).toBeInTheDocument();
  });
});
