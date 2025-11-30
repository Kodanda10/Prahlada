import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, type Mock } from 'vitest';
import React from 'react';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import RouteGuard from '../../components/RouteGuard';
import useAuth from '../../hooks/useAuth';
import PageLoader from '../../components/PageLoader';

// Mock the useAuth hook
vi.mock('../../hooks/useAuth', () => ({
  default: vi.fn(),
}));

// Mock PageLoader component since its internal logic is not under test here
vi.mock('../../components/PageLoader', () => ({
  default: () => <div data-testid="page-loader">Loading...</div>,
}));

describe('RouteGuard Component', () => {
  const mockUseAuth = useAuth as Mock;

  it('renders PageLoader when authentication status is loading', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false, status: 'loading' });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/protected" element={<RouteGuard>Protected Content</RouteGuard>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByTestId('page-loader')).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('redirects to login when not authenticated', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false, status: 'idle' });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/login" element={<div>Login Page</div>} />
          <Route path="/protected" element={<RouteGuard>Protected Content</RouteGuard>} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Login Page')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });

  it('renders children when authenticated', () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: true, status: 'idle' });

    render(
      <MemoryRouter initialEntries={['/protected']}>
        <Routes>
          <Route path="/protected" element={<RouteGuard>Protected Content</RouteGuard>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(screen.queryByTestId('page-loader')).not.toBeInTheDocument();
  });

  it('redirects to a custom login path if redirectTo prop is provided', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false, status: 'idle' });

    render(
      <MemoryRouter initialEntries={['/admin-protected']}>
        <Routes>
          <Route path="/custom-login" element={<div>Custom Login Page</div>} />
          <Route path="/admin-protected" element={<RouteGuard redirectTo="/custom-login">Admin Content</RouteGuard>} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Custom Login Page')).toBeInTheDocument();
      expect(screen.queryByText('Admin Content')).not.toBeInTheDocument();
    });
  });

  it('preserves current location in state for redirection back after login', async () => {
    mockUseAuth.mockReturnValue({ isAuthenticated: false, status: 'idle' });

    const MockLoginPage = () => {
      const location = useLocation();
      const from = location.state?.from?.pathname || '/';
      return <div data-testid="login-page">Login Page from {from}</div>;
    };

    render(
      <MemoryRouter initialEntries={['/some-protected-path']}>
        <Routes>
          <Route path="/login" element={<MockLoginPage />} />
          <Route path="/some-protected-path" element={<RouteGuard>Protected Content</RouteGuard>} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => {
      expect(screen.getByTestId('login-page')).toBeInTheDocument();
      expect(screen.getByText('Login Page from /some-protected-path')).toBeInTheDocument();
      expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    });
  });
});
