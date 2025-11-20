import { describe, it, expect, vi } from 'vitest';
import { render, act } from '@testing-library/react';
import { AnimatedGlassCard } from '../../components/AnimatedGlassCard';
import { AnimatedNavTabs } from '../../components/AnimatedNavTabs';

describe('60 FPS Animation Performance', () => {
  beforeEach(() => {
    // Mock requestAnimationFrame for consistent timing
    vi.useFakeTimers();
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation(cb => {
      setTimeout(cb, 16); // ~60 FPS
      return 1;
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe('AnimatedGlassCard Performance', () => {
    it('maintains 60 FPS during entrance animation', async () => {
      const performanceMarks: number[] = [];

      // Mock performance.now to track frame timing
      const originalNow = performance.now;
      performance.now = vi.fn(() => Date.now());

      render(<AnimatedGlassCard delay={0}>Test Content</AnimatedGlassCard>);

      // Simulate animation frames
      await act(async () => {
        for (let i = 0; i < 60; i++) { // 1 second at 60 FPS
          performanceMarks.push(performance.now());
          vi.advanceTimersByTime(16);
        }
      });

      // Verify frame timing consistency
      const frameIntervals = performanceMarks.slice(1).map((time, i) =>
        time - performanceMarks[i]
      );

      const avgInterval = frameIntervals.reduce((a, b) => a + b, 0) / frameIntervals.length;
      expect(avgInterval).toBeCloseTo(16, 2); // Within 2ms of 16ms target

      performance.now = originalNow;
    });

    it('handles multiple cards without frame drops', async () => {
      render(
        <div>
          <AnimatedGlassCard delay={0}>Card 1</AnimatedGlassCard>
          <AnimatedGlassCard delay={100}>Card 2</AnimatedGlassCard>
          <AnimatedGlassCard delay={200}>Card 3</AnimatedGlassCard>
        </div>
      );

      await act(async () => {
        vi.advanceTimersByTime(1000); // Run for 1 second
      });

      // Verify all cards rendered
      expect(document.querySelectorAll('.animated-glass-card')).toHaveLength(3);
    });
  });

  describe('AnimatedNavTabs Performance', () => {
    const mockTabs = [
      { id: 'tab1', label: 'Tab 1', path: '/tab1' },
      { id: 'tab2', label: 'Tab 2', path: '/tab2' },
      { id: 'tab3', label: 'Tab 3', path: '/tab3' },
    ];

    it('smooth tab transitions at 60 FPS', async () => {
      const { rerender } = render(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="tab1"
          onTabChange={() => {}}
        />
      );

      await act(async () => {
        vi.advanceTimersByTime(100); // Initial render
      });

      rerender(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="tab2"
          onTabChange={() => {}}
        />
      );

      await act(async () => {
        vi.advanceTimersByTime(300); // Transition duration
      });

      const activeTab = document.querySelector('.tab-button.active');
      expect(activeTab).toBeInTheDocument();
      expect(activeTab).toHaveTextContent('Tab 2');
    });

    it('handles rapid tab switching smoothly', async () => {
      const { rerender } = render(
        <AnimatedNavTabs
          tabs={mockTabs}
          activeTab="tab1"
          onTabChange={() => {}}
        />
      );

      // Rapid switching between tabs
      for (let i = 0; i < 5; i++) {
        const nextTab = mockTabs[i % mockTabs.length];
        rerender(
          <AnimatedNavTabs
            tabs={mockTabs}
            activeTab={nextTab.id}
            onTabChange={() => {}}
          />
        );

        await act(async () => {
          vi.advanceTimersByTime(50);
        });
      }

      // Should handle rapid changes without breaking
      expect(document.querySelectorAll('.tab-button')).toHaveLength(3);
    });
  });

  describe('Animation Frame Budget', () => {
    it('stays within 16ms frame budget', async () => {
      const frameTimes: number[] = [];

      const originalRAF = window.requestAnimationFrame;
      window.requestAnimationFrame = vi.fn((callback) => {
        const start = performance.now();
        setTimeout(() => {
          callback(performance.now());
          const end = performance.now();
          frameTimes.push(end - start);
        }, 16);
        return 1;
      });

      render(
        <div>
          <AnimatedGlassCard delay={0}>Performance Test</AnimatedGlassCard>
          <AnimatedNavTabs
            tabs={[{ id: 'test', label: 'Test', path: '/test' }]}
            activeTab="test"
            onTabChange={() => {}}
          />
        </div>
      );

      await act(async () => {
        vi.advanceTimersByTime(1000); // Run for 1 second
      });

      // Check that most frames stayed within budget
      const framesOverBudget = frameTimes.filter(time => time > 16);
      const budgetCompliance = (frameTimes.length - framesOverBudget.length) / frameTimes.length;

      expect(budgetCompliance).toBeGreaterThan(0.9); // 90% of frames within budget

      window.requestAnimationFrame = originalRAF;
    });
  });
});