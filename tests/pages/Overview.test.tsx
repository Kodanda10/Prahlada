import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Overview from '../../pages/Overview';
import React from 'react';

describe('Overview Page', () => {
  it('renders overview content', () => {
    render(<Overview />);
    expect(screen.getByRole('generic')).toBeInTheDocument();
  });
});
