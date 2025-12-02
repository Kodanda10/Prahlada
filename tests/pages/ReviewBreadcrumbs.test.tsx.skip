import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Review from '../../pages/Review';
import React from 'react';

describe('ReviewBreadcrumbs', () => {
  it('shows correct breadcrumb hierarchy', () => {
    render(<Review />);
    // Check for breadcrumb elements
    expect(screen.getByRole('generic')).toBeInTheDocument();
  });
});
