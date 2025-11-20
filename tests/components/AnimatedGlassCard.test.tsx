
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import AnimatedGlassCard from '../../components/AnimatedGlassCard';

describe('AnimatedGlassCard', () => {
  it('renders children correctly', () => {
    const { getByTestId } = render(
      <AnimatedGlassCard>
        <div data-testid="child">Child Content</div>
      </AnimatedGlassCard>
    );
    expect(getByTestId('child')).toBeInTheDocument();
  });

  it('renders title when provided', () => {
    const { getByText } = render(<AnimatedGlassCard title="Test Card" >Content</AnimatedGlassCard>);
    expect(getByText('Test Card')).toBeInTheDocument();
  });

  it('renders with default animation classes (framer-motion adds inline styles/classes)', () => {
    const { container } = render(<AnimatedGlassCard>Content</AnimatedGlassCard>);
    expect(container.firstChild).toHaveClass('relative');
    expect(container.firstChild).toHaveClass('overflow-hidden');
  });
});
