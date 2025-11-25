import { apiService } from './api';

export interface TelemetryEvent {
  type: 'error' | 'action' | 'performance' | 'navigation';
  name: string;
  data?: Record<string, any>;
  timestamp?: number;
  url?: string;
}

export const telemetryService = {
  logError: async (error: Error, errorInfo?: any) => {
    console.error('Telemetry Error:', error);
    try {
      await apiService.post('/api/telemetry', {
        type: 'error',
        name: error.name,
        data: {
          message: error.message,
          stack: error.stack,
          componentStack: errorInfo?.componentStack,
        },
        url: window.location.href,
        timestamp: Date.now(),
      });
    } catch (e) {
      // Fail silently to avoid loops
      console.warn('Failed to send telemetry error:', e);
    }
  },

  logAction: async (action: string, details?: any) => {
    try {
      await apiService.post('/api/telemetry', {
        type: 'action',
        name: action,
        data: details,
        url: window.location.href,
        timestamp: Date.now(),
      });
    } catch (e) {
      console.warn('Failed to send telemetry action:', e);
    }
  },

  logPerformance: async (metric: string, value: number) => {
    try {
      await apiService.post('/api/telemetry', {
        type: 'performance',
        name: metric,
        data: { value },
        url: window.location.href,
        timestamp: Date.now(),
      });
    } catch (e) {
      console.warn('Failed to send telemetry performance:', e);
    }
  },
  
  logNavigation: async (path: string) => {
      try {
          await apiService.post('/api/telemetry', {
              type: 'navigation',
              name: 'route_change',
              data: { path },
              timestamp: Date.now()
          });
      } catch (e) {
          console.warn('Failed to send telemetry navigation:', e);
      }
  }
};
