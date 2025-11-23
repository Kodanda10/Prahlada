import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import useAuth from '../hooks/useAuth';
import PageLoader from './PageLoader';

interface RouteGuardProps {
  children: React.ReactNode;
  redirectTo?: string;
}

const RouteGuard: React.FC<RouteGuardProps> = ({ children, redirectTo = '/login' }) => {
  const { isAuthenticated, status } = useAuth();
  const location = useLocation();

  if (status === 'loading') {
    return <PageLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate to={redirectTo} state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default RouteGuard;
