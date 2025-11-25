import { AuthAPI, setApiAuthToken } from './api';

export const TOKEN_KEY = 'dhruv_auth_token';

export const authService = {
  login: async (username: string, password: string) => {
    const response = await AuthAPI.login(username, password);
    if (response.token) {
      localStorage.setItem(TOKEN_KEY, response.token);
      setApiAuthToken(response.token);
    }
    return response;
  },

  logout: () => {
    localStorage.removeItem(TOKEN_KEY);
    setApiAuthToken(null);
    window.location.href = '/login';
  },

  getToken: () => {
    return localStorage.getItem(TOKEN_KEY);
  },

  isAuthenticated: () => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) return false;
    
    // Basic expiry check (decoding without verify signature on client)
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      if (payload.exp && payload.exp * 1000 < Date.now()) {
        authService.logout();
        return false;
      }
      return true;
    } catch {
      return false;
    }
  },

  // Security utility functions
  sanitizeInput: (input: string): string => {
    // Basic sanitization to prevent XSS
    return input
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  },

  validateInput: (input: string): boolean => {
    // Simple check for common SQL injection patterns
    const sqlPatterns = [
      /;\s*DROP\s+TABLE/i,
      /--/,
      /'\s*OR\s*'1'='1/i,
      /;\s*--/
    ];
    return !sqlPatterns.some(pattern => pattern.test(input));
  },

  validateToken: (token: string): boolean => {
    // Check for standard JWT structure: header.payload.signature
    if (!token || typeof token !== 'string') return false;
    const parts = token.split('.');
    if (parts.length !== 3) return false;
    
    try {
      // Verify payload is base64 decodable
      JSON.parse(atob(parts[1]));
      return true;
    } catch {
      return false;
    }
  }
};
