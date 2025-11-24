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

// Strip motion-only props so React DOM warnings don't fire in tests
const stripMotionProps = (props: Record<string, unknown>) => {
  const clean = { ...props };
  [
    'initial',
    'animate',
    'exit',
    'whileHover',
    'whileTap',
    'whileInView',
    'transition',
    'layoutId',
    'variants',
  ].forEach((key) => delete (clean as any)[key]);
  return clean;
};

// Minimal framer-motion mock for components that need it
vi.mock('framer-motion', () => ({
  AnimatePresence: ({ children }: any) => React.createElement(React.Fragment, null, children),
  motion: new Proxy(
    {},
    {
      get: (_, prop) => {
        return ({ children, ...props }: any) =>
          React.createElement(prop as string, stripMotionProps(props), children);
      },
    },
  ),
  useInView: () => true, // Always return true for tests
  useMotionValue: (initial = 0) => {
    let value = initial;
    const listeners: Array<(v: number) => void> = [];
    return {
      get: () => value,
      set: (v: number) => {
        value = v;
        listeners.forEach((listener) => listener(v));
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

// Mock react-map-gl to avoid Mapbox browser support errors in jsdom
vi.mock('react-map-gl', () => {
  const React = require('react');
  const MockMap = ({ children, ...props }: any) => {
    const {
      mapboxAccessToken,
      mapStyle,
      initialViewState,
      onMove,
      onMouseEnter,
      onMouseLeave,
      onLoad,
      interactiveLayerIds,
      ...rest
    } = props;
    return React.createElement('div', { 'data-testid': 'mock-map', ...rest }, children);
  };
  const Marker = ({ children, ...props }: any) =>
    React.createElement('div', { 'data-testid': 'mock-map-marker', ...props }, children);
  const NavigationControl = (props: any) =>
    React.createElement('div', { 'data-testid': 'mock-map-nav', ...props });
  const GeolocateControl = (props: any) =>
    React.createElement('div', { 'data-testid': 'mock-map-geo', ...props });
  const ScaleControl = (props: any) =>
    React.createElement('div', { 'data-testid': 'mock-map-scale', ...props });
  const FullscreenControl = (props: any) =>
    React.createElement('div', { 'data-testid': 'mock-map-fullscreen', ...props });
  const Layer = ({ children, ...props }: any) =>
    React.createElement('div', { 'data-testid': 'mock-map-layer', ...props }, children);
  const Source = ({ children, ...props }: any) =>
    React.createElement('div', { 'data-testid': 'mock-map-source', ...props }, children);
  return {
    __esModule: true,
    default: MockMap,
    Marker,
    NavigationControl,
    GeolocateControl,
    ScaleControl,
    FullscreenControl,
    Layer,
    Source,
  };
});
