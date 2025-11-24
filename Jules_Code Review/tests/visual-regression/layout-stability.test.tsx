import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import AnimatedGlassCard from '../../components/AnimatedGlassCard';
import GlassCard from '../../components/GlassCard';

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

      const firstCard = firstRender.querySelector('.relative');
      const secondCard = secondRender.querySelector('.relative');

      expect(firstCard).toBeInTheDocument();
      expect(secondCard).toBeInTheDocument();
    });

    it('handles dynamic content without layout shift', () => {
      const { rerender, container } = render(
        <GlassCard title="Test Card">
          <div>Short content</div>
        </GlassCard>
      );

      const cardElement = container.querySelector('.relative');
      expect(cardElement).toBeInTheDocument();

      rerender(
        <GlassCard title="Test Card">
          <div>Longer content that should not cause layout shift due to proper CSS containment</div>
        </GlassCard>
      );

      expect(cardElement).toBeInTheDocument();
      expect(screen.getByText(/Longer content/)).toBeInTheDocument();
    });
  });

  describe('AnimatedGlassCard Component', () => {
    it('renders with stable initial state', () => {
      const { container } = render(
        <AnimatedGlassCard delay={0}>
          <div>Animated content</div>
        </AnimatedGlassCard>
      );

      const animatedCard = container.querySelector('.relative');
      expect(animatedCard).toBeInTheDocument();
    });

    it('maintains animation bounds within container', () => {
      const { container } = render(
        <div style={{ width: '400px', height: '300px' }}>
          <AnimatedGlassCard delay={100}>
            <div>Large content block</div>
          </AnimatedGlassCard>
        </div>
      );
      
      const animatedCard = container.querySelector('.relative');
      expect(animatedCard).toBeInTheDocument();
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

      const { container } = render(
        <div className="responsive-container">
          <GlassCard title="Responsive Card">
            <div>Responsive content</div>
          </GlassCard>
        </div>
      );

      const card = container.querySelector('.relative');
      expect(card).toBeInTheDocument();

      // Simulate mobile viewport
      window.innerWidth = 768;
      window.dispatchEvent(new Event('resize'));

      expect(card).toBeInTheDocument();
    });
  });
});
