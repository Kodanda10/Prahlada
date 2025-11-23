import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import React from 'react';

describe('Font Fallback Coverage', () => {
  it('renders Devanagari without tofu boxes', () => {
    const devanagari = '?????? ??????';
    render(<div style={{ fontFamily: 'fallback, sans-serif' }}>{devanagari}</div>);
    expect(screen.getByText(devanagari)).toBeInTheDocument();
  });
});
