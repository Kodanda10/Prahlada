import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AnalyticsDashboard from '../../pages/Analytics';
import React from 'react';

describe('SemanticRegionsHindi', () => {
  it('has Hindi aria-labels', () => {
    render(<AnalyticsDashboard />);
    // Check for aria attributes with Hindi content
    expect(screen.getByText('????? ?????? ????????')).toBeInTheDocument();
  });
});
