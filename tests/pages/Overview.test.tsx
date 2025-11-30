import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Overview from '../../pages/Overview';
import React from 'react';

describe('Overview Page', () => {
  it('renders overview content', async () => {
    render(<Overview />);
    expect(await screen.findByText(/डैशबोर्ड सारांश/i, {}, { timeout: 2000 })).toBeInTheDocument();
    expect(screen.getByText(/सिस्टम की स्थिति/i)).toBeInTheDocument();
  });
});
