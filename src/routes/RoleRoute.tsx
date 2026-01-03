/**
 * Role Route Component
 * Restricts routes based on user role
 */

import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types/user';
import { ROUTES } from '../utils/constants';

interface RoleRouteProps {
  children: React.ReactNode;
  allowedRoles: UserRole[];
}

export const RoleRoute: React.FC<RoleRouteProps> = ({ children, allowedRoles }) => {
  const { user } = useAuth();

  if (!user || !allowedRoles.includes(user.role)) {
    // Redirect to appropriate dashboard based on role
    const redirectTo = user?.role === 'ADMIN' ? ROUTES.ADMIN_DASHBOARD : ROUTES.EMPLOYEE_DASHBOARD;
    return <Navigate to={redirectTo} replace />;
  }

  return <>{children}</>;
};
