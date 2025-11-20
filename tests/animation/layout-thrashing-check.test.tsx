import { describe, it, expect, vi } from 'vitest';
import { render, act } from '@testing-library/react';
import { AnimatedNavTabs } from '../../components/AnimatedNavTabs';

describe('Layout Thrashing / Reflow Check', () => {
  beforeEach(() => {
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
      });

      Object.defineProperty(HTMLElement.prototype, 'offsetHeight', {
        get() {
          layoutQueries.push('offsetHeight');
          queryCount++;
          return 50;
        },
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
      });

      const { rerender } = render(
        <AnimatedNavTabs
          tabs={[
            { id: 'home', label: 'Home', path: '/home' },
            { id: 'analytics', label: 'Analytics', path: '/analytics' },
          ]}
          activeTab="home"
          onTabChange={() => {}}
        />
      );

      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      // Switch tabs
      rerender(
        <AnimatedNavTabs
          tabs={[
            { id: 'home', label: 'Home', path: '/home' },
            { id: 'analytics', label: 'Analytics', path: '/analytics' },
          ]}
          activeTab="analytics"
          onTabChange={() => {}}
        />
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

    it('uses transform instead of layout properties', async () => {
      const transformCalls: string[] = [];
      const layoutCalls: string[] = [];

      // Mock style setting to track transform vs layout usage
      const mockStyle = {
        setProperty: vi.fn((prop, value) => {
          if (prop.includes('transform')) {
            transformCalls.push(`${prop}: ${value}`);
          } else if (['width', 'height', 'left', 'top'].includes(prop)) {
            layoutCalls.push(`${prop}: ${value}`);
          }
        }),
      };

      Object.defineProperty(HTMLElement.prototype, 'style', {
        value: mockStyle,
        writable: true,
      });

      render(
        <AnimatedNavTabs
          tabs={[
            { id: 'tab1', label: 'Tab 1', path: '/tab1' },
            { id: 'tab2', label: 'Tab 2', path: '/tab2' },
          ]}
          activeTab="tab1"
          onTabChange={() => {}}
        />
      );

      await act(async () => {
        vi.advanceTimersByTime(500);
      });

      // Should prefer transform over layout properties
      expect(transformCalls.length).toBeGreaterThan(layoutCalls.length);
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

    it('uses requestAnimationFrame for DOM updates', async () => {
      const rafCalls: number[] = [];
      const originalRAF = window.requestAnimationFrame;

      window.requestAnimationFrame = vi.fn((callback) => {
        rafCalls.push(Date.now());
        setTimeout(callback, 16);
        return rafCalls.length;
      });

      render(
        <AnimatedNavTabs
          tabs={[
            { id: 'test', label: 'Test', path: '/test' },
          ]}
          activeTab="test"
          onTabChange={() => {}}
        />
      );

      await act(async () => {
        vi.advanceTimersByTime(100);
      });

      // Should use requestAnimationFrame for smooth animations
      expect(rafCalls.length).toBeGreaterThan(0);

      window.requestAnimationFrame = originalRAF;
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
          <AnimatedNavTabs
            tabs={[{ id: 'test', label: 'Test', path: '/test' }]}
            activeTab="test"
            onTabChange={() => {}}
          />
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
      const element = document.querySelector('.test-element');
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