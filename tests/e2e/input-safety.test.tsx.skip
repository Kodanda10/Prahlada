import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import React from 'react';

describe('Mixed-Script Input Safety', () => {
  it('handles mixed Hindi-English input', () => {
    const mixed = 'Raigarh ??????';
    render(<div>{mixed}</div>);
    expect(screen.getByText(mixed)).toBeInTheDocument();
  });
});
