import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import GlassCard from '../../components/GlassCard';
import React from 'react';

describe('GlassCard', () => {
  it('renders children correctly', () => {
    render(<GlassCard><p>Content</p></GlassCard>);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('has glassmorphism classes', () => {
    const { container } = render(<GlassCard><div>Test</div></GlassCard>);
    expect(container.firstChild).toHaveClass('backdrop-blur-xl', 'bg-white/10');
  });
});
