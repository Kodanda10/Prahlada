import { ParsedEvent, Stats } from '../types';
import { AllowedEventFilter, normalizeEventFilter, redactSensitiveLogData } from '../utils/security';

// Points to the FastAPI backend; prefer env override and HTTPS when available
const resolveApiBase = () => {
  const envBase = import.meta.env.VITE_API_BASE?.trim();

  const isLocal = (url: string) =>
    url.includes('localhost') ||
    url.includes('127.0.0.1') ||
    url.startsWith('http://0.0.0.0') ||
    url.startsWith('http://[::1]');

  if (envBase) {
    if (!envBase.startsWith('https://') && !isLocal(envBase)) {
      console.warn('Insecure API base detected; consider using HTTPS in production');
    }
    return envBase.replace(/\/+$/, '');
  }

  if (typeof window !== 'undefined' && window.location?.origin) {
    const origin = window.location.origin;
    const defaultPort = origin.includes('localhost') ? '8000' : '';
    const base = defaultPort ? `${origin.replace(/:\\d+$/, '')}:${defaultPort}` : origin;
    return base.replace(/\/+$/, '');
  }

  return 'http://localhost:8000';
};

const API_BASE = resolveApiBase();

type HeadersObject = Record<string, string>;

let authToken: string | null = null;

export interface AuthUser {
  id: string;
  username: string;
  roles: string[];
  displayName?: string;
  email?: string;
  [key: string]: unknown;
}

export interface AuthResponse {
  token: string;
  user: AuthUser;
}

export const setApiAuthToken = (token: string | null) => {
  authToken = token;
};

const normalizeHeaders = (headers?: HeadersInit): HeadersObject => {
  if (!headers) return {};

  if (Array.isArray(headers)) {
    return headers.reduce<HeadersObject>((acc, [key, value]) => {
      acc[key] = value;
      return acc;
    }, {});
  }

  if (typeof Headers !== 'undefined' && headers instanceof Headers) {
    const acc: HeadersObject = {};
    headers.forEach((value, key) => {
      acc[key] = value;
    });
    return acc;
  }

  return { ...(headers as HeadersObject) };
};

const withAuth = (init: RequestInit = {}): RequestInit => {
  const headers = normalizeHeaders(init.headers);
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }
  return {
    ...init,
    headers,
  };
};

const parseJson = async <T>(response: Response, context: string): Promise<T> => {
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const payload = await response.json();
      if (payload?.message) {
        errorMessage = payload.message;
      }
    } catch {
      // Ignore JSON parse failures for error bodies
    }
    throw new Error(errorMessage);
  }

  return (await response.json()) as T;
};

const logApiError = (context: string, error: unknown) => {
  const safeContext = redactSensitiveLogData({ context });
  console.error('API Error', safeContext, error);
};

export async function fetchStats(): Promise<Stats> {
  try {
    const res = await fetch(`${API_BASE}/api/stats`, withAuth());
    if (!res.ok) throw new Error('Failed to fetch stats');
    return await res.json();
  } catch (error) {
    logApiError('stats', error);
    return {
      total_tweets: 0,
      parsed_success: 0,
      pending: 0,
      errors: 0
    };
  }
}

export async function fetchEvents(filter: AllowedEventFilter | string = 'all'): Promise<ParsedEvent[]> {
  try {
    const safeFilter = normalizeEventFilter(filter);
    const url = new URL(`${API_BASE}/api/events`);
    if (safeFilter === 'failed') {
      url.searchParams.append('status', 'FAILED');
    }
    const res = await fetch(url.toString(), withAuth());
    if (!res.ok) throw new Error('Failed to fetch events');
    const data = await res.json();
    return data;
  } catch (error) {
    logApiError('events', error);
    return [];
  }
}

export async function fetchAnalyticsData(type: 'event-types' | 'districts') {
  try {
    const res = await fetch(`${API_BASE}/api/analytics/${type}`, withAuth());
    if (!res.ok) throw new Error(`Failed to fetch analytics ${type}`);
    return await res.json();
  } catch (error) {
    logApiError(`analytics-${type}`, error);
    return [];
  }
}

// API Service object for tests
export const apiService = {
  async get(endpoint: string) {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, withAuth());
      return await parseJson(res, `GET ${endpoint}`);
    } catch (error) {
      logApiError(`get-${endpoint}`, error);
      throw error;
    }
  },

  async post(endpoint: string, data: any) {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, withAuth({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      }));
      return await parseJson(res, `POST ${endpoint}`);
    } catch (error) {
      logApiError(`post-${endpoint}`, error);
      throw error;
    }
  },

  async put(endpoint: string, data: any) {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, withAuth({
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      }));
      return await parseJson(res, `PUT ${endpoint}`);
    } catch (error) {
      logApiError(`put-${endpoint}`, error);
      throw error;
    }
  },

  async delete(endpoint: string) {
    try {
      const res = await fetch(`${API_BASE}${endpoint}`, withAuth({
        method: 'DELETE',
      }));
      return await parseJson(res, `DELETE ${endpoint}`);
    } catch (error) {
      logApiError(`delete-${endpoint}`, error);
      throw error;
    }
  }
};

const normalizeAuthResponse = (payload: unknown): AuthResponse => {
  if (!payload || typeof payload !== 'object') {
    throw new Error('Invalid authentication response');
  }

  const { token, user } = payload as { token?: string; user?: Partial<AuthUser> };

  if (!token || !user || typeof user.username !== 'string') {
    throw new Error('Authentication payload missing required fields');
  }

  return {
    token,
    user: {
      ...user,
      id: String(user.id ?? user.username),
      username: user.username,
      roles: Array.isArray(user.roles) ? user.roles.map(String) : [],
      displayName: typeof user.displayName === 'string' ? user.displayName : undefined,
      email: typeof user.email === 'string' ? user.email : undefined,
    },
  };
};

export const AuthAPI = {
  async login(username: string, password: string): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE}/api/auth/login`, withAuth({
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    }));

    const payload = await parseJson<AuthResponse>(response, 'POST /api/auth/login');
    return normalizeAuthResponse(payload);
  },
};
