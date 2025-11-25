import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Events from '../../pages/Events';
import React from 'react';

describe('Events Page', () => {
  it('renders events dashboard', () => {
    render(<Events />);
    expect(screen.getByRole('generic')).toBeInTheDocument();
  });
});
