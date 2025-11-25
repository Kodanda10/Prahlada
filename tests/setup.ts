import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';

// Minimal setup - only essential global mocks for performance
vi.stubGlobal('matchMedia', vi.fn().mockImplementation(query => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(), // deprecated
  removeListener: vi.fn(), // deprecated
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
})));

// Mock Recharts globally
vi.mock('recharts', () => {
  const React = require('react');
  const OriginalModule = vi.importActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children, width, height }: any) =>
      React.createElement('div', { style: { width: width || 800, height: height || 800 } },
        React.Children.map(children, (child: any) =>
          React.cloneElement(child, { width: width || 800, height: height || 800 })
        )
      ),
    PieChart: ({ children, width, height }: any) => React.createElement('svg', { width: width || 800, height: height || 400, 'data-testid': 'pie-chart' }, children),
    Pie: () => React.createElement('g', null, 'Pie Chart'),
    BarChart: ({ children, width, height }: any) => React.createElement('svg', { width: width || 800, height: height || 400, 'data-testid': 'bar-chart' }, children),
    Bar: () => React.createElement('g', null, 'Bar Chart'),
    XAxis: () => React.createElement('g', null, 'XAxis'),
    YAxis: () => React.createElement('g', null, 'YAxis'),
    Tooltip: () => React.createElement('div', null, 'Tooltip'),
    Legend: () => React.createElement('div', null, 'Legend'),
    Cell: () => React.createElement('g', null, 'Cell'),
    CartesianGrid: () => React.createElement('g', null, 'CartesianGrid'),
    AreaChart: ({ children, width, height }: any) => React.createElement('svg', { width: width || 800, height: height || 400, 'data-testid': 'area-chart' }, children),
    Area: () => React.createElement('g', null, 'Area Chart'),
    LineChart: ({ children, width, height }: any) => React.createElement('svg', { width: width || 800, height: height || 400, 'data-testid': 'line-chart' }, children),
    Line: () => React.createElement('g', null, 'Line Chart'),
  };
});

// Simple global mocks
global.ResizeObserver = class {
  observe() { }
  unobserve() { }
  disconnect() { }
};

global.IntersectionObserver = class {
  constructor() { }
  observe() { }
  disconnect() { }
  unobserve() { }
};

// Mock SVG methods for D3 interactions in jsdom
if (typeof SVGElement !== 'undefined') {
  if (!SVGElement.prototype.getScreenCTM) {
    SVGElement.prototype.getScreenCTM = () => {
      return {
        a: 1, b: 0, c: 0, d: 1, e: 0, f: 0,
        multiply: () => ({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 }),
        inverse: () => ({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 }),
        translate: () => ({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 }),
        scale: () => ({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 }),
        rotate: () => ({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 }),
      } as DOMMatrix;
    };
  }
  
  // Some D3 versions check ownerSVGElement or similar
  Object.defineProperty(SVGElement.prototype, 'ownerSVGElement', {
    get: function() { return this.closest('svg'); }
  });
  
  // Mock viewBox for D3 zoom on SVGElement too, as backup
  Object.defineProperty(SVGElement.prototype, 'viewBox', {
    get: function() {
      return {
        baseVal: {
          x: 0,
          y: 0,
          width: parseInt(this.getAttribute('width') || '0'),
          height: parseInt(this.getAttribute('height') || '0'),
        },
        animVal: {
          x: 0,
          y: 0,
          width: parseInt(this.getAttribute('width') || '0'),
          height: parseInt(this.getAttribute('height') || '0'),
        },
      };
    },
    configurable: true,
  });
}

if (typeof SVGSVGElement !== 'undefined') {
  if (!SVGSVGElement.prototype.createSVGPoint) {
    SVGSVGElement.prototype.createSVGPoint = function() {
      return {
        x: 0, y: 0,
        matrixTransform: function(matrix: DOMMatrix) {
          return { x: this.x, y: this.y };
        }
      } as DOMPoint;
    };
  }
  // Mock viewBox for D3 zoom
  Object.defineProperty(SVGSVGElement.prototype, 'viewBox', {
    get: function() {
      return {
        baseVal: {
          x: 0,
          y: 0,
          width: parseInt(this.getAttribute('width') || '0'),
          height: parseInt(this.getAttribute('height') || '0'),
        },
        animVal: {
          x: 0,
          y: 0,
          width: parseInt(this.getAttribute('width') || '0'),
          height: parseInt(this.getAttribute('height') || '0'),
        },
      };
    },
    configurable: true,
  });
}

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

// Mock localStorage
const localStorageMock = (function() {
  let store: Record<string, string> = {};
  return {
    getItem: function(key: string) {
      return store[key] || null;
    },
    setItem: function(key: string, value: string) {
      store[key] = value.toString();
    },
    removeItem: function(key: string) {
      delete store[key];
    },
    clear: function() {
      store = {};
    },
    key: function(index: number) {
      return Object.keys(store)[index] || null;
    },
    get length() {
      return Object.keys(store).length;
    }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

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

    React.useEffect(() => {
      if (onLoad) {
        onLoad({ target: {} });
      }
    }, [onLoad]);

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

// Mock lucide-react icons
vi.mock('lucide-react', async (importOriginal) => {
  const actual = await importOriginal<typeof import('lucide-react')>();
  const mocks = Object.keys(actual).reduce((acc, key) => {
    acc[key] = (props: any) => {
      const React = require('react');
      return React.createElement('svg', {
        'data-testid': `icon-${key}`,
        ...props
      });
    };
    return acc;
  }, {} as any);
  return mocks;
});
