import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Home from '../../pages/Home';
import React from 'react';

describe('Home Page', () => {
  it('renders the main dashboard', () => {
    render(<Home />);
    // Check for some expected content
    expect(screen.getByRole('generic')).toBeInTheDocument();
  });
});
