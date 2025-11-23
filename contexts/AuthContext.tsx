import React, { createContext, useCallback, useEffect, useMemo, useState } from 'react';
import { AuthAPI, AuthResponse, setApiAuthToken } from '../services/api';

type AuthStatus = 'idle' | 'loading' | 'error';

interface AuthContextValue {
  token: string | null;
  user: AuthResponse['user'] | null;
  isAuthenticated: boolean;
  status: AuthStatus;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const STORAGE_KEY = 'project-dhruv/auth';

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthResponse['user'] | null>(null);
  const [status, setStatus] = useState<AuthStatus>('loading');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const session = JSON.parse(stored) as { token: string; user: AuthResponse['user'] };
        setToken(session.token);
        setUser(session.user);
        setApiAuthToken(session.token);
      }
    } catch (storageError) {
      console.warn('Failed to hydrate auth session', storageError);
      localStorage.removeItem(STORAGE_KEY);
    } finally {
      setStatus('idle');
    }
  }, []);

  const persistSession = useCallback((session: { token: string; user: AuthResponse['user'] }) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(session));
  }, []);

  const clearSession = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setStatus('loading');
    setError(null);
    try {
      const response = await AuthAPI.login(username, password);
      setToken(response.token);
      setUser(response.user);
      setApiAuthToken(response.token);
      persistSession({ token: response.token, user: response.user });
      setStatus('idle');
    } catch (authError) {
      setStatus('error');
      const message = authError instanceof Error ? authError.message : 'Authentication failed';
      setError(message);
      throw authError;
    }
  }, [persistSession]);

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
    setApiAuthToken(null);
    clearSession();
    setError(null);
    setStatus('idle');
  }, [clearSession]);

  const value = useMemo<AuthContextValue>(
    () => ({
      token,
      user,
      isAuthenticated: Boolean(token),
      status,
      error,
      login,
      logout,
    }),
    [token, user, status, error, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
