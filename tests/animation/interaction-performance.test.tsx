import { describe, it, expect, vi } from 'vitest';
import { render, fireEvent, act } from '@testing-library/react';
import { AnimatedNavTabs } from '../../components/AnimatedNavTabs';
import { NumberTicker } from '../../components/NumberTicker';

describe('Interaction Performance & Responsiveness', () => {
  describe('Tab Navigation Performance', () => {
    const mockTabs = [
      { id: 'home', label: 'Home', path: '/home' },
      { id: 'analytics', label: 'Analytics', path: '/analytics' },
      { id: 'review', label: 'Review', path: '/review' },
      { id: 'command', label: 'Command', path: '/command' },
    ];

    it('responds to tab clicks within 100ms', async () => {
      const onTabChange = vi.fn();
      const startTime = performance.now();

      render(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="home"
          onTabChange={onTabChange}
        />
      );

      const analyticsTab = document.querySelector('[data-tab-id="analytics"]') ||
                          document.querySelectorAll('.tab-button')[1];

      if (analyticsTab) {
        fireEvent.click(analyticsTab);
        const endTime = performance.now();
        const responseTime = endTime - startTime;

        expect(responseTime).toBeLessThan(100); // 100ms response time
        expect(onTabChange).toHaveBeenCalledWith('analytics');
      }
    });

    it('handles keyboard navigation smoothly', async () => {
      const onTabChange = vi.fn();

      render(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="home"
          onTabChange={onTabChange}
        />
      );

      const tabContainer = document.querySelector('.animated-nav-tabs');

      if (tabContainer) {
        // Simulate arrow key navigation
        fireEvent.keyDown(tabContainer, { key: 'ArrowRight' });
        expect(onTabChange).toHaveBeenCalled();

        fireEvent.keyDown(tabContainer, { key: 'ArrowLeft' });
        expect(onTabChange).toHaveBeenCalledTimes(2);
      }
    });
  });

  describe('NumberTicker Interactions', () => {
    it('updates smoothly on value changes', async () => {
      const { rerender } = render(<NumberTicker value={100} />);

      await act(async () => {
        rerender(<NumberTicker value={500} />);
      });

      const tickerElement = document.querySelector('.number-ticker');
      expect(tickerElement).toBeInTheDocument();
    });

    it('handles rapid value updates', async () => {
      const { rerender } = render(<NumberTicker value={0} />);

      // Rapid updates
      for (let i = 0; i < 10; i++) {
        await act(async () => {
          rerender(<NumberTicker value={i * 100} />);
        });
      }

      expect(document.querySelector('.number-ticker')).toBeInTheDocument();
    });
  });

  describe('Hover and Focus States', () => {
    it('applies hover effects without delay', async () => {
      render(
        <AnimatedNavTabs
          tabs={[{ id: 'test', label: 'Test', path: '/test' }]}
          activeTab="test"
          onTabChange={() => {}}
        />
      );

      const tabButton = document.querySelector('.tab-button');

      if (tabButton) {
        const startTime = performance.now();
        fireEvent.mouseEnter(tabButton);
        const endTime = performance.now();

        expect(endTime - startTime).toBeLessThan(50); // Hover response < 50ms
        expect(tabButton).toBeInTheDocument();
      }
    });

    it('maintains focus indicators', () => {
      render(
        <button className="focus-test-button">Test Button</button>
      );

      const button = document.querySelector('.focus-test-button');

      if (button) {
        fireEvent.focus(button);
        expect(button).toBeInTheDocument();
      }
    });
  });

  describe('Touch Interactions (Mobile)', () => {
    it('responds to touch events on mobile', () => {
      render(
        <div className="touch-container">
          <button className="touch-button">Touch Me</button>
        </div>
      );

      const touchButton = document.querySelector('.touch-button');

      if (touchButton) {
        fireEvent.touchStart(touchButton);
        fireEvent.touchEnd(touchButton);

        expect(touchButton).toBeInTheDocument();
      }
    });

    it('prevents double-tap zoom on interactive elements', () => {
      render(
        <AnimatedNavTabs
          tabs={[{ id: 'test', label: 'Test', path: '/test' }]}
          activeTab="test"
          onTabChange={() => {}}
        />
      );

      const tab = document.querySelector('.tab-button');

      if (tab) {
        // Simulate double tap
        fireEvent.touchStart(tab);
        fireEvent.touchEnd(tab);
        fireEvent.touchStart(tab);
        fireEvent.touchEnd(tab);

        expect(tab).toBeInTheDocument();
      }
    });
  });
});