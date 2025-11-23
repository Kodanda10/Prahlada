import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';

// Minimal setup - only essential global mocks for performance
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: () => ({
    matches: false,
    media: '',
    onchange: null,
    addListener: () => {},
    removeListener: () => {},
    addEventListener: () => {},
    removeEventListener: () => {},
    dispatchEvent: () => {},
  }),
});

// Simple global mocks
global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};

global.IntersectionObserver = class {
  constructor() {}
  observe() {}
  disconnect() {}
  unobserve() {}
};

// Minimal framer-motion mock for components that need it
vi.mock('framer-motion', () => ({
  AnimatePresence: ({ children }: any) => React.createElement(React.Fragment, null, children),
  motion: new Proxy({}, {
    get: (_, prop) => ({ children, ...props }: any) =>
      React.createElement(prop as string, props, children),
  }),
  useInView: () => true, // Always return true for tests
  useMotionValue: (initial = 0) => {
    let value = initial;
    const listeners: Array<(v: number) => void> = [];
    return {
      get: () => value,
      set: (v: number) => {
        value = v;
        listeners.forEach(listener => listener(v));
      },
      on: (event: string, callback: (v: number) => void) => {
        if (event === 'change') {
          listeners.push(callback);
          // Immediately call with current value
          callback(value);
        }
        return () => {
          const index = listeners.indexOf(callback);
          if (index > -1) listeners.splice(index, 1);
        };
      },
    };
  },
  useSpring: (source: any) => source || { get: () => 0 },
  useTransform: (value: any) => value,
  useAnimation: () => ({ start: vi.fn(), stop: vi.fn() }),
}));
