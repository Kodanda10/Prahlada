import '@testing-library/jest-dom';

// Mock ResizeObserver for Recharts/Framer
globalThis.ResizeObserver = class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
};