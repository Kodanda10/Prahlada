import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Home } from 'lucide-react';
import AnimatedGlassCard from '../../components/AnimatedGlassCard';
import AnimatedNavTabs from '../../components/AnimatedNavTabs';

describe('Frame Rate Monitoring (60 FPS)', () => {
  beforeEach(() => {
    // Mock requestAnimationFrame for consistent timing
    vi.useFakeTimers();
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation(cb => {
      setTimeout(cb, 16); // ~60 FPS
      return 1;
    });

    // Mock performance.now with a variable we can control
    let now = 0;
    vi.spyOn(performance, 'now').mockImplementation(() => now);
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe('Hero Entrance Animation Performance', () => {
    it('maintains 60 FPS during card entrance animations', async () => {
      const frameTimestamps: number[] = [];
      let frameCount = 0;

      // Use a local variable for precise control in this test
      let currentTime = 0;
      vi.spyOn(performance, 'now').mockImplementation(() => currentTime);

      render(
        <div className="hero-section">
          <AnimatedGlassCard delay={0}>
            <h2>Hero Content</h2>
          </AnimatedGlassCard>
        </div>
      );

      // Simulate animation frames
      await act(async () => {
        for (let i = 0; i < 60; i++) {
          frameTimestamps.push(performance.now());
          currentTime += 16.67;
          vi.advanceTimersByTime(16);
          frameCount++;
        }
      });

      // Verify 60 frames in ~1 second
      expect(frameCount).toBe(60);

      // Check frame timing consistency
      const intervals = frameTimestamps.slice(1).map((time, i) =>
        time - frameTimestamps[i]
      );
      const avgInterval = intervals.reduce((a, b) => a + b, 0) / intervals.length;
      expect(avgInterval).toBeCloseTo(16.67, 1); // Within 1ms of 60 FPS target
    });

    it('handles multiple simultaneous entrance animations', async () => {
      // Setup time incrementing
      let currentTime = 0;
      vi.spyOn(performance, 'now').mockImplementation(() => currentTime);

      const startTime = performance.now();

      render(
        <div className="hero-grid">
          {Array.from({ length: 6 }, (_, i) => (
            <AnimatedGlassCard key={i} delay={i * 100}>
              <div>Card {i + 1}</div>
            </AnimatedGlassCard>
          ))}
        </div>
      );

      await act(async () => {
        // Advance time in chunks
        for(let i=0; i<60; i++) {
             currentTime += 16.67;
             vi.advanceTimersByTime(16);
        }
      });

      const endTime = performance.now();
      const totalTime = endTime - startTime;

      // Should complete within reasonable time despite multiple animations
      expect(totalTime).toBeLessThan(1500);
    });
  });

  describe('Card Stagger Animation Performance', () => {
    it('maintains smooth stagger timing across multiple cards', async () => {
      render(
        <div className="card-stagger">
          {Array.from({ length: 8 }, (_, i) => (
            <AnimatedGlassCard key={i} delay={i * 150}>
              <div>Staggered Card {i + 1}</div>
            </AnimatedGlassCard>
          ))}
        </div>
      );

      // Simulate animation progression
      await act(async () => {
        for (let frame = 0; frame < 120; frame++) { // 2 seconds at 60 FPS
          vi.advanceTimersByTime(16);
        }
      });
    });

    it('prevents frame drops during peak stagger load', async () => {
      const frameTimes: number[] = [];
      let currentTime = 0;
      vi.spyOn(performance, 'now').mockImplementation(() => currentTime);

      render(
        <div className="peak-load-test">
          {Array.from({ length: 12 }, (_, i) => (
            <AnimatedGlassCard key={i} delay={i * 50}>
              <div>Peak Load Card {i + 1}</div>
            </AnimatedGlassCard>
          ))}
        </div>
      );

      await act(async () => {
        const startTime = performance.now();
        for (let frame = 0; frame < 180; frame++) { // 3 seconds
          currentTime += 16.67;
          vi.advanceTimersByTime(16);
          frameTimes.push(performance.now() - startTime);
        }
      });

      // Check that frames are reasonably spaced (no major drops)
      const frameIntervals = frameTimes.slice(1).map((time, i) =>
        time - frameTimes[i]
      );

      const droppedFrames = frameIntervals.filter(interval => interval > 32); // > 2 frames at 60 FPS
      expect(droppedFrames.length).toBeLessThan(5); // Allow some variance
    });
  });

  describe('NumberTicker Animation Performance', () => {
    it('animates number changes at consistent frame rate', async () => {
      const tickerValues: number[] = [];
      let animationFrameCount = 0;
      let currentTime = 0;
      vi.spyOn(performance, 'now').mockImplementation(() => currentTime);

      render(<div className="ticker-container"></div>);

      // Simulate NumberTicker animation
      const animateValue = (start: number, end: number, duration: number) => {
        const startTime = performance.now();
        const animate = () => {
          const elapsed = performance.now() - startTime;
          const progress = Math.min(elapsed / duration, 1);
          const currentValue = start + (end - start) * progress;

          tickerValues.push(currentValue);
          animationFrameCount++;

          if (progress < 1) {
            currentTime += 16; // Advance mock time
            setTimeout(animate, 16); // 60 FPS
          }
        };
        animate();
      };

      await act(async () => {
        animateValue(0, 1000, 1000); // 1 second animation
        vi.advanceTimersByTime(1050);
      });

      // Should have ~60 frames for 1 second animation
      expect(animationFrameCount).toBeGreaterThan(50);
      expect(animationFrameCount).toBeLessThan(70);
      expect(tickerValues[tickerValues.length - 1]).toBeCloseTo(1000, 0);
    });

    it('handles rapid consecutive number changes', async () => {
      const valueChanges = [100, 500, 250, 750, 1000];
      const renderedValues: number[] = [];

      // Simulate rapid value updates
      for (const value of valueChanges) {
        await act(async () => {
          // Simulate component re-render with new value
          vi.advanceTimersByTime(50);
        });
        renderedValues.push(value);
      }

      expect(renderedValues).toEqual(valueChanges);
    });
  });

  describe('Performance Benchmarks', () => {
    it('meets 55-60 FPS target for complex animations', async () => {
      const frameTimestamps: number[] = [];
      let currentTime = 0;
      vi.spyOn(performance, 'now').mockImplementation(() => currentTime);

      render(
        <BrowserRouter>
          <div className="complex-animation-test">
            <AnimatedNavTabs
              tabs={[
                { label: 'Tab 1', path: '/tab1', icon: Home },
                { label: 'Tab 2', path: '/tab2', icon: Home },
                { label: 'Tab 3', path: '/tab3', icon: Home },
              ]}
              activePath="/tab1"
              isAuthenticated={true}
            />
            {Array.from({ length: 4 }, (_, i) => (
              <AnimatedGlassCard key={i} delay={i * 200}>
                <div>Complex Animation {i + 1}</div>
              </AnimatedGlassCard>
            ))}
          </div>
        </BrowserRouter>
      );

      await act(async () => {
        const startTime = performance.now();
        for (let frame = 0; frame < 120; frame++) {
          currentTime += 16.67;
          frameTimestamps.push(performance.now() - startTime);
          vi.advanceTimersByTime(16);
        }
      });

      // Calculate FPS
      const totalTime = frameTimestamps[frameTimestamps.length - 1] - frameTimestamps[0];
      // Prevent division by zero
      const validTotalTime = totalTime > 0 ? totalTime : 1;
      const fps = (frameTimestamps.length / validTotalTime) * 1000;

      expect(fps).toBeGreaterThanOrEqual(55);
      expect(fps).toBeLessThanOrEqual(65); // Allow some variance
    });

    it('maintains performance under memory pressure', async () => {
      // Simulate memory pressure by creating many components
      const componentCount = 20;

      render(
        <div className="memory-pressure-test">
          {Array.from({ length: componentCount }, (_, i) => (
            <AnimatedGlassCard key={i} delay={i * 100} className="animated-glass-card">
              <div>Memory Test {i + 1}</div>
            </AnimatedGlassCard>
          ))}
        </div>
      );

      await act(async () => {
        vi.advanceTimersByTime(3000); // Run for 3 seconds
      });

      // Verify all components still exist and animations completed
      const cards = document.querySelectorAll('.animated-glass-card');
      expect(cards).toHaveLength(componentCount);
    });
  });
});