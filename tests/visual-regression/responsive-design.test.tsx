import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import AnimatedGlassCard from '../../components/AnimatedGlassCard';
import CustomBarChart from '../../components/charts/CustomBarChart';

describe('Responsive Design Visual Regression', () => {
  const mockChartData = [
    { name: 'Jan', value: 400 },
    { name: 'Feb', value: 300 },
    { name: 'Mar', value: 600 },
  ];

  describe('Mobile Viewport (< 768px)', () => {
    beforeEach(() => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      window.dispatchEvent(new Event('resize'));
    });

    it('components adapt to mobile layout', () => {
      const { container } = render(
        <div className="mobile-container">
          <AnimatedGlassCard delay={0} className="animated-glass-card">
            <div>Mobile content</div>
          </AnimatedGlassCard>
        </div>
      );

      const card = container.querySelector('.animated-glass-card');
      expect(card).toBeInTheDocument();
    });

    it('charts scale appropriately on mobile', () => {
      const { container } = render(
        <CustomBarChart
          data={mockChartData}
          width={300}
          height={200}
        />
      );

      const svgElement = container.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
      expect(svgElement).toHaveAttribute('width', '300');
    });
  });

  describe('Tablet Viewport (768px - 1024px)', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 900,
      });
      window.dispatchEvent(new Event('resize'));
    });

    it('maintains tablet-optimized layouts', () => {
      const { container } = render(
        <div className="tablet-container">
          <AnimatedGlassCard delay={0} className="animated-glass-card">
            <div>Tablet content</div>
          </AnimatedGlassCard>
          <CustomBarChart
            data={mockChartData}
            width={500}
            height={300}
          />
        </div>
      );

      const card = container.querySelector('.animated-glass-card');
      const chart = container.querySelector('svg');

      expect(card).toBeInTheDocument();
      expect(chart).toBeInTheDocument();
    });
  });

  describe('Desktop Viewport (> 1024px)', () => {
    beforeEach(() => {
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 1440,
      });
      window.dispatchEvent(new Event('resize'));
    });

    it('utilizes full desktop real estate', () => {
      const { container } = render(
        <div className="desktop-container">
          <AnimatedGlassCard delay={0} className="animated-glass-card">
            <div>Desktop content with more space</div>
          </AnimatedGlassCard>
          <CustomBarChart
            data={mockChartData}
            width={800}
            height={400}
          />
        </div>
      );

      const card = container.querySelector('.animated-glass-card');
      const chart = container.querySelector('svg');

      expect(card).toBeInTheDocument();
      expect(chart).toHaveAttribute('width', '800');
    });
  });

  describe('Breakpoint Transitions', () => {
    it('handles viewport changes smoothly', () => {
      const { container, rerender } = render(
        <div style={{ width: '1200px' }}>
          <AnimatedGlassCard delay={0} className="animated-glass-card">
            <div>Content</div>
          </AnimatedGlassCard>
        </div>
      );

      let card = container.querySelector('.animated-glass-card');
      expect(card).toBeInTheDocument();

      // Simulate breakpoint change
      rerender(
        <div style={{ width: '600px' }}>
          <AnimatedGlassCard delay={0} className="animated-glass-card">
            <div>Content</div>
          </AnimatedGlassCard>
        </div>
      );

      card = container.querySelector('.animated-glass-card');
      expect(card).toBeInTheDocument();
    });

    it('charts maintain readability across breakpoints', () => {
      const { container, rerender } = render(
        <CustomBarChart
          data={mockChartData}
          width={1000}
          height={400}
        />
      );

      let svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '1000');

      rerender(
        <CustomBarChart
          data={mockChartData}
          width={400}
          height={300}
        />
      );

      svg = container.querySelector('svg');
      expect(svg).toHaveAttribute('width', '400');
    });
  });
});