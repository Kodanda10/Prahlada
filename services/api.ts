
import { ParsedEvent, Stats } from '../types';

// Points to the FastAPI backend
// Ensure your backend is running on port 8000
const API_BASE = 'http://localhost:8000';

export async function fetchStats(): Promise<Stats> {
  try {
    const res = await fetch(`${API_BASE}/api/stats`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return await res.json();
  } catch (error) {
    console.error('API Error (Stats):', error);
    return {
      total_tweets: 0,
      parsed_success: 0,
      pending: 0,
      errors: 0
    };
  }
}

export async function fetchEvents(filter: string = 'all'): Promise<ParsedEvent[]> {
  try {
    const url = new URL(`${API_BASE}/api/events`);
    if (filter === 'failed') {
      url.searchParams.append('status', 'FAILED');
    }
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch events');
    const data = await res.json();
    return data;
  } catch (error) {
    console.error('API Error (Events):', error);
    return [];
  }
}

export async function fetchAnalyticsData(type: 'event-types' | 'districts') {
  try {
    const res = await fetch(`${API_BASE}/api/analytics/${type}`);
    if (!res.ok) throw new Error(`Failed to fetch analytics ${type}`);
    return await res.json();
  } catch (error) {
    console.error(`API Error (Analytics - ${type}):`, error);
    return [];
  }
}

// API Service object for tests
export const apiService = {
  async get(endpoint: string) {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`);
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json();
    } catch (error) {
      console.error('API GET Error:', error);
      throw error;
    }
  },

  async post(endpoint: string, data: any) {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json();
    } catch (error) {
      console.error('API POST Error:', error);
      throw error;
    }
  },

  async put(endpoint: string, data: any) {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json();
    } catch (error) {
      console.error('API PUT Error:', error);
      throw error;
    }
  },

  async delete(endpoint: string) {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'DELETE',
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      }
      return await res.json();
    } catch (error) {
      console.error('API DELETE Error:', error);
      throw error;
    }
  }
};
