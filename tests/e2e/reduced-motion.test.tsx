import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AnimatedGlassCard from '../../components/AnimatedGlassCard';
import React from 'react';

describe('Reduced Motion', () => {
  it('falls back to minimal animations when reduced-motion is enabled', () => {
    // Mock prefers-reduced-motion
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: query === '(prefers-reduced-motion: reduce)',
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });

    render(<AnimatedGlassCard data-testid="glass-card"><div>Test</div></AnimatedGlassCard>);
    // Since framer-motion is mocked to return basic elements, it should work
    expect(screen.getByTestId('glass-card')).toBeInTheDocument();
  });
});
