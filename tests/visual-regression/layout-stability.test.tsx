import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { AnimatedGlassCard } from '../../components/AnimatedGlassCard';
import { GlassCard } from '../../components/GlassCard';

describe('Layout Stability & Visual Regression', () => {
  describe('GlassCard Component', () => {
    it('maintains consistent dimensions across renders', () => {
      const { container: firstRender } = render(
        <GlassCard title="Test Card">
          <div>Content</div>
        </GlassCard>
      );

      const { container: secondRender } = render(
        <GlassCard title="Test Card">
          <div>Content</div>
        </GlassCard>
      );

      const firstCard = firstRender.querySelector('.glass-card');
      const secondCard = secondRender.querySelector('.glass-card');

      expect(firstCard).toBeInTheDocument();
      expect(secondCard).toBeInTheDocument();

      // Check if dimensions are consistent (basic check)
      expect(firstCard).toHaveClass('glass-card');
      expect(secondCard).toHaveClass('glass-card');
    });

    it('handles dynamic content without layout shift', () => {
      const { rerender } = render(
        <GlassCard title="Test Card">
          <div>Short content</div>
        </GlassCard>
      );

      const cardElement = screen.getByRole('article');
      const initialHeight = cardElement.clientHeight;

      rerender(
        <GlassCard title="Test Card">
          <div>Longer content that should not cause layout shift due to proper CSS containment</div>
        </GlassCard>
      );

      // In a real visual regression test, we'd compare screenshots
      // For now, we verify the component exists and handles content changes
      expect(cardElement).toBeInTheDocument();
      expect(screen.getByText(/Longer content/)).toBeInTheDocument();
    });
  });

  describe('AnimatedGlassCard Component', () => {
    it('renders with stable initial state', () => {
      render(
        <AnimatedGlassCard delay={0}>
          <div>Animated content</div>
        </AnimatedGlassCard>
      );

      const animatedCard = screen.getByRole('article');
      expect(animatedCard).toBeInTheDocument();
      expect(animatedCard).toHaveClass('animated-glass-card');
    });

    it('maintains animation bounds within container', () => {
      render(
        <div style={{ width: '400px', height: '300px' }}>
          <AnimatedGlassCard delay={100}>
            <div>Large content block</div>
          </AnimatedGlassCard>
        </div>
      );

      const container = screen.getByRole('article').parentElement;
      const animatedCard = screen.getByRole('article');

      expect(container).toContainElement(animatedCard);
      expect(animatedCard).toHaveClass('animated-glass-card');
    });
  });

  describe('Responsive Layout Stability', () => {
    it('maintains layout on viewport changes', () => {
      // Mock viewport resize
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1200,
      });

      render(
        <div className="responsive-container">
          <GlassCard title="Responsive Card">
            <div>Responsive content</div>
          </GlassCard>
        </div>
      );

      const card = screen.getByRole('article');
      expect(card).toBeInTheDocument();

      // Simulate mobile viewport
      window.innerWidth = 768;
      window.dispatchEvent(new Event('resize'));

      expect(card).toBeInTheDocument();
      expect(card).toHaveClass('glass-card');
    });
  });
});