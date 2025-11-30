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
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return '';
    }
    // For non-localhost, keep existing logic or default to origin
    return window.location.origin.replace(/\/+$/, '');
  }

  return '';
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
    const url = new URL(`${API_BASE}/api/events`, window.location.origin);
    if (safeFilter === 'failed') {
      url.searchParams.append('status', 'FAILED');
    }
    const res = await fetch(url.toString(), withAuth());
    if (!res.ok) throw new Error(`Failed to fetch events: ${res.status} ${res.statusText}`);
    const rawData = await res.json();

    // Map backend EventResponse to frontend ParsedEvent
    return rawData.map((item: any) => ({
      tweet_id: item.tweet_id,
      author_handle: 'unknown', // Not in EventResponse
      raw_text: item.raw_text,
      text: item.raw_text,
      created_at: item.created_at,
      processing_status: item.parsing_status,
      fetched_at: item.created_at,
      processed_at: item.created_at,
      is_parsed: true,
      parsed_event_id: item.tweet_id,
      review_status: 'pending', // Default
      export_timestamp: new Date().toISOString(),
      export_version: 'v8',
      is_clean: true,
      metadata_v8: {
        model: 'gemini-1.5-flash',
        processing_time_ms: 0,
        version: 'v8'
      },
      parsed_data_v8: {
        event_type: item.event_type?.[0] || 'Unknown',
        event_type_secondary: item.event_type?.slice(1) || [],
        event_date: item.created_at,
        location: {
          canonical: item.location_text,
          district: null,
          location_type: '',
        },
        people_mentioned: item.people_mentioned || [],
        people_canonical: item.people_mentioned || [],
        schemes_mentioned: item.scheme_tags || [],
        word_buckets: item.word_buckets || [],
        target_groups: [],
        communities: [],
        organizations: [],
        hierarchy_path: [],
        visit_count: 0,
        vector_embedding_id: null,
        confidence: 0.8,
        review_status: 'pending',
        needs_review: true,
        content_mode: 'original',
        is_other_original: false,
        is_rescued_other: false,
        rescue_tag: null,
        rescue_confidence_bonus: 0,
        semantic_location_used: false,
        location_type: ''
      },
      approved_by_human: false
    }));
  } catch (error) {
    logApiError('events', error);
    throw error;
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
  },

  async approveTweet(tweetId: string) {
    try {
      const res = await fetch(`${API_BASE}/api/events/${tweetId}/approve`, withAuth({
        method: 'POST',
      }));
      return await parseJson(res, `POST /api/events/${tweetId}/approve`);
    } catch (error) {
      logApiError(`approve-${tweetId}`, error);
      throw error;
    }
  },

  async updateEvent(tweetId: string, parsedData: any) {
    try {
      const res = await fetch(`${API_BASE}/api/events/${tweetId}`, withAuth({
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ parsed_data: parsedData }),
      }));
      return await parseJson(res, `PUT /api/events/${tweetId}`);
    } catch (error) {
      logApiError(`update-${tweetId}`, error);
      throw error;
    }
  },
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
