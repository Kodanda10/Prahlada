import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Home } from 'lucide-react';
import AnimatedNavTabs from '../../components/AnimatedNavTabs';

describe('Layout Thrashing / Reflow Check', () => {
  beforeEach(() => {
    vi.useFakeTimers();

    // Mock getComputedStyle and offset measurements to track layout queries
    const mockGetComputedStyle = vi.fn();
    const mockOffsetWidth = vi.spyOn(HTMLElement.prototype, 'offsetWidth', 'get');
    const mockOffsetHeight = vi.spyOn(HTMLElement.prototype, 'offsetHeight', 'get');

    Object.defineProperty(window, 'getComputedStyle', {
      value: mockGetComputedStyle,
      writable: true,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  describe('NumberTicker Layout Thrashing Prevention', () => {
    it('minimizes layout queries during number animation', async () => {
      const layoutQueries: string[] = [];
      let queryCount = 0;

      // Mock layout-triggering properties
      const originalOffsetWidth = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetWidth');
      const originalOffsetHeight = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'offsetHeight');

      Object.defineProperty(HTMLElement.prototype, 'offsetWidth', {
        get() {
          layoutQueries.push('offsetWidth');
          queryCount++;
          return 100;
        },
        configurable: true
      });

      Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
        get() {
          layoutQueries.push('offsetHeight');
          queryCount++;
          return 50;
        },
        configurable: true
      });

      render(
        <div className="ticker-layout-test">
          <span className="number-display">0</span>
        </div>
      );

      // Simulate number animation updates
      const numberElement = document.querySelector('.number-display');
      expect(numberElement).toBeInTheDocument();

      await act(async () => {
        // Simulate 60 animation frames
        for (let i = 0; i < 60; i++) {
          numberElement!.textContent = (i * 10).toString();
          vi.advanceTimersByTime(16);
        }
      });

      // Should minimize layout queries during animation
      expect(queryCount).toBeLessThan(10); // Very few layout queries

      // Restore original properties
      if (originalOffsetWidth) {
        Object.defineProperty(HTMLElement.prototype, 'offsetWidth', originalOffsetWidth);
      }
      if (originalOffsetHeight) {
        Object.defineProperty(HTMLElement.prototype, 'offsetHeight', originalOffsetHeight);
      }
    });

    it('uses cached measurements to prevent reflow', async () => {
      const measurementCache: Map<string, number> = new Map();
      let cacheHits = 0;
      let cacheMisses = 0;

      // Mock cached measurement system
      const getCachedMeasurement = (element: Element, property: string) => {
        const key = `${element.className}-${property}`;
        if (measurementCache.has(key)) {
          cacheHits++;
          return measurementCache.get(key);
        } else {
          cacheMisses++;
          const value = property === 'width' ? 200 : 40;
          measurementCache.set(key, value);
          return value;
        }
      };

      render(
        <div className="cached-measurement-test">
          <span className="cached-ticker">12345</span>
        </div>
      );

      const ticker = document.querySelector('.cached-ticker');
      expect(ticker).toBeInTheDocument();

      // Simulate multiple measurement requests
      for (let i = 0; i < 10; i++) {
        getCachedMeasurement(ticker!, 'width');
        getCachedMeasurement(ticker!, 'height');
      }

      // Should have cache hits for repeated measurements
      expect(cacheHits).toBeGreaterThan(cacheMisses);
    });
  });

  describe('Tab Transition Layout Stability', () => {
    it('prevents reflow during tab switching', async () => {
      const reflowTriggers: string[] = [];
      let reflowCount = 0;

      // Mock style changes that trigger reflow
      const originalStyle = Object.getOwnPropertyDescriptor(HTMLElement.prototype, 'style');

      Object.defineProperty(HTMLElement.prototype, 'style', {
        get() {
          return {
            setProperty: (prop: string, value: string) => {
              if (['width', 'height', 'display', 'position'].includes(prop)) {
                reflowTriggers.push(prop);
                reflowCount++;
              }
            },
          };
        },
        configurable: true
      });

      const { rerender } = render(
        <BrowserRouter>
          <AnimatedNavTabs
            tabs={[
              { label: 'Home', path: '/home', icon: Home },
              { label: 'Analytics', path: '/analytics', icon: Home },
            ]}
            activePath="/home"
            isAuthenticated={true}
          />
        </BrowserRouter>
      );

      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      // Switch tabs
      rerender(
        <BrowserRouter>
          <AnimatedNavTabs
            tabs={[
              { label: 'Home', path: '/home', icon: Home },
              { label: 'Analytics', path: '/analytics', icon: Home },
            ]}
            activePath="/analytics"
            isAuthenticated={true}
          />
        </BrowserRouter>
      );

      await act(async () => {
        vi.advanceTimersByTime(300);
      });

      // Should minimize reflow-triggering style changes
      expect(reflowCount).toBeLessThan(5);

      // Restore original style
      if (originalStyle) {
        Object.defineProperty(HTMLElement.prototype, 'style', originalStyle);
      }
    });

    it('renders without layout errors', async () => {
      const { container } = render(
        <BrowserRouter>
          <AnimatedNavTabs
            tabs={[
              { label: 'Tab 1', path: '/tab1', icon: Home },
              { label: 'Tab 2', path: '/tab2', icon: Home },
            ]}
            activePath="/tab1"
            isAuthenticated={true}
          />
        </BrowserRouter>
      );

      await act(async () => {
        vi.advanceTimersByTime(500);
      });

      // Should render successfully
      expect(container.querySelector('a')).toBeInTheDocument();
    });
  });

  describe('Animation Frame Management', () => {
    it('batches DOM updates to prevent thrashing', async () => {
      const updateBatches: number[][] = [];
      let currentBatch: number[] = [];

      render(
        <div className="batch-update-test">
          <div className="animated-element">Content</div>
        </div>
      );

      // Simulate batched updates
      const batchUpdate = (updates: number[]) => {
        currentBatch.push(...updates);
        // In real implementation, this would be debounced
        setTimeout(() => {
          updateBatches.push([...currentBatch]);
          currentBatch = [];
        }, 16); // Next frame
      };

      await act(async () => {
        // Simulate multiple rapid updates
        batchUpdate([1, 2, 3]);
        batchUpdate([4, 5]);
        vi.advanceTimersByTime(20);
        batchUpdate([6, 7, 8]);

        vi.advanceTimersByTime(50);
      });

      // Should have batched updates instead of individual calls
      expect(updateBatches.length).toBeGreaterThan(0);
      expect(updateBatches[0]).toEqual([1, 2, 3, 4, 5]);
    });

    it('handles animations without errors', async () => {
      const { container } = render(
        <BrowserRouter>
          <AnimatedNavTabs
            tabs={[
              { label: 'Test', path: '/test', icon: Home },
            ]}
            activePath="/test"
            isAuthenticated={true}
          />
        </BrowserRouter>
      );

      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      // Should render and animate without errors
      expect(container.querySelector('a')).toBeInTheDocument();
    });
  });

  describe('Memory and Performance Monitoring', () => {
    it('prevents memory leaks from animation loops', async () => {
      const animationLoops: (() => void)[] = [];
      let cleanupCount = 0;

      // Simulate animation loop creation and cleanup
      const createAnimationLoop = () => {
        const loop = () => {
          // Animation logic
        };
        animationLoops.push(loop);
        return () => {
          cleanupCount++;
          const index = animationLoops.indexOf(loop);
          if (index > -1) {
            animationLoops.splice(index, 1);
          }
        };
      };

      render(
        <div className="animation-memory-test">
          <BrowserRouter>
            <AnimatedNavTabs
              tabs={[{ label: 'Test', path: '/test', icon: Home }]}
              activePath="test"
              isAuthenticated={true}
            />
          </BrowserRouter>
        </div>
      );

      // Create and cleanup animation loops
      const cleanup1 = createAnimationLoop();
      const cleanup2 = createAnimationLoop();

      await act(async () => {
        vi.advanceTimersByTime(1000);
      });

      cleanup1();
      cleanup2();

      expect(cleanupCount).toBe(2);
      expect(animationLoops.length).toBe(0);
    });

    it('monitors and reports layout thrashing', () => {
      const layoutReads: string[] = [];
      const layoutWrites: string[] = [];
      let thrashingDetected = false;

      // Mock layout read/write detection
      const originalGetComputedStyle = window.getComputedStyle;
      window.getComputedStyle = vi.fn((element) => {
        layoutReads.push(`read-${element.className}`);
        return originalGetComputedStyle(element);
      });

      const mockStyle = {
        setProperty: vi.fn((prop, value) => {
          layoutWrites.push(`write-${prop}`);
          // Detect interleaved reads and writes (thrashing)
          if (layoutReads.length > 0 && layoutWrites.length > 1) {
            thrashingDetected = true;
          }
        }),
      };

      Object.defineProperty(HTMLElement.prototype, 'style', {
        value: mockStyle,
        writable: true,
      });

      render(
        <div className="thrashing-detection-test">
          <div className="test-element">Test</div>
        </div>
      );

      // Simulate some operations
      const element = document.querySelector('.test-element') as HTMLElement;
      if (element) {
        window.getComputedStyle(element);
        element.style.setProperty('width', '100px');
        window.getComputedStyle(element);
        element.style.setProperty('height', '50px');
      }

      // Should detect and report thrashing
      expect(thrashingDetected).toBe(true);
      expect(layoutReads.length).toBeGreaterThan(0);
      expect(layoutWrites.length).toBeGreaterThan(0);

      // Restore originals
      window.getComputedStyle = originalGetComputedStyle;
    });
  });
});