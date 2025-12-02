import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Ingestion from '../../pages/Ingestion';
import React from 'react';

describe('Ingestion Page', () => {
  it('renders ingestion interface', () => {
    render(<Ingestion />);
    expect(screen.getByRole('generic')).toBeInTheDocument();
  });
});
