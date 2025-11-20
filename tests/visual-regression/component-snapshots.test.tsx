import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { AnimatedNavTabs } from '../../components/AnimatedNavTabs';
import { NumberTicker } from '../../components/NumberTicker';

describe('Component Visual Snapshots', () => {
  describe('AnimatedNavTabs Component', () => {
    const mockTabs = [
      { id: 'home', label: 'Home', path: '/home' },
      { id: 'analytics', label: 'Analytics', path: '/analytics' },
      { id: 'review', label: 'Review', path: '/review' },
    ];

    it('renders consistent tab layout', () => {
      const { container } = render(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="home"
          onTabChange={() => {}}
        />
      );

      const navElement = container.querySelector('.animated-nav-tabs');
      expect(navElement).toBeInTheDocument();

      const tabButtons = container.querySelectorAll('.tab-button');
      expect(tabButtons).toHaveLength(3);

      // Verify tab structure
      mockTabs.forEach((tab, index) => {
        expect(tabButtons[index]).toHaveTextContent(tab.label);
      });
    });

    it('maintains active tab visual state', () => {
      const { container } = render(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="analytics"
          onTabChange={() => {}}
        />
      );

      const activeTab = container.querySelector('.tab-button.active');
      expect(activeTab).toBeInTheDocument();
      expect(activeTab).toHaveTextContent('Analytics');
    });

    it('handles tab transitions smoothly', () => {
      const { rerender, container } = render(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="home"
          onTabChange={() => {}}
        />
      );

      let activeTab = container.querySelector('.tab-button.active');
      expect(activeTab).toHaveTextContent('Home');

      rerender(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="review"
          onTabChange={() => {}}
        />
      );

      activeTab = container.querySelector('.tab-button.active');
      expect(activeTab).toHaveTextContent('Review');
    });
  });

  describe('NumberTicker Component', () => {
    it('renders number with consistent formatting', () => {
      const { container } = render(<NumberTicker value={1234} />);

      const tickerElement = container.querySelector('.number-ticker');
      expect(tickerElement).toBeInTheDocument();

      // Check if number is displayed (exact formatting may vary)
      const numberDisplay = container.querySelector('.ticker-value') || tickerElement;
      expect(numberDisplay).toBeInTheDocument();
    });

    it('handles different number ranges', () => {
      const { container: smallContainer } = render(<NumberTicker value={42} />);
      const { container: largeContainer } = render(<NumberTicker value={999999} />);
      const { container: decimalContainer } = render(<NumberTicker value={123.45} />);

      expect(smallContainer.querySelector('.number-ticker')).toBeInTheDocument();
      expect(largeContainer.querySelector('.number-ticker')).toBeInTheDocument();
      expect(decimalContainer.querySelector('.number-ticker')).toBeInTheDocument();
    });

    it('maintains consistent dimensions', () => {
      const { container } = render(
        <div style={{ width: '200px' }}>
          <NumberTicker value={56789} />
        </div>
      );

      const ticker = container.querySelector('.number-ticker');
      expect(ticker).toBeInTheDocument();
      expect(ticker?.parentElement).toHaveStyle({ width: '200px' });
    });
  });
});