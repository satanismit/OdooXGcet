/**
 * App Routes Component
 * Main routing configuration
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ProtectedRoute } from './ProtectedRoute';
import { RoleRoute } from './RoleRoute';
import { ROUTES } from '../utils/constants';

// Auth Pages
import { Login } from '../pages/auth/Login';
import { Register } from '../pages/auth/Register';
import { VerifyEmail } from '../pages/auth/VerifyEmail';

// Dashboard Pages
import { EmployeeDashboard } from '../pages/dashboard/EmployeeDashboard';
import { AdminDashboard } from '../pages/dashboard/AdminDashboard';

// Profile Pages
import { ViewProfile } from '../pages/profile/ViewProfile';
import { EditProfile } from '../pages/profile/EditProfile';

// Feature Pages
import { Attendance } from '../pages/attendance/Attendance';
import { MyLeaves } from '../pages/leave/MyLeaves';
import { LeaveApprovals } from '../pages/leave/LeaveApprovals';
import { MySalary } from '../pages/payroll/MySalary';
import { PayrollAdmin } from '../pages/payroll/PayrollAdmin';

// Other
import { NotFound } from '../pages/NotFound';

export const AppRoutes: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <Routes>
      {/* Public Routes */}
      <Route
        path={ROUTES.LOGIN}
        element={isAuthenticated ? <Navigate to={user?.role === 'ADMIN' ? ROUTES.ADMIN_DASHBOARD : ROUTES.EMPLOYEE_DASHBOARD} replace /> : <Login />}
      />
      <Route
        path={ROUTES.REGISTER}
        element={isAuthenticated ? <Navigate to={ROUTES.EMPLOYEE_DASHBOARD} replace /> : <Register />}
      />
      <Route path={ROUTES.VERIFY_EMAIL} element={<VerifyEmail />} />

      {/* Protected Routes - Employee */}
      <Route
        path={ROUTES.EMPLOYEE_DASHBOARD}
        element={
          <ProtectedRoute>
            <RoleRoute allowedRoles={['EMPLOYEE']}>
              <EmployeeDashboard />
            </RoleRoute>
          </ProtectedRoute>
        }
      />

      {/* Protected Routes - Admin */}
      <Route
        path={ROUTES.ADMIN_DASHBOARD}
        element={
          <ProtectedRoute>
            <RoleRoute allowedRoles={['ADMIN']}>
              <AdminDashboard />
            </RoleRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.LEAVE_APPROVALS}
        element={
          <ProtectedRoute>
            <RoleRoute allowedRoles={['ADMIN']}>
              <LeaveApprovals />
            </RoleRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.PAYROLL_ADMIN}
        element={
          <ProtectedRoute>
            <RoleRoute allowedRoles={['ADMIN']}>
              <PayrollAdmin />
            </RoleRoute>
          </ProtectedRoute>
        }
      />

      {/* Protected Routes - Common */}
      <Route
        path="/profile/:id"
        element={
          <ProtectedRoute>
            <ViewProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.PROFILE_VIEW}
        element={
          <ProtectedRoute>
            <ViewProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path="/profile/edit/:id"
        element={
          <ProtectedRoute>
            <RoleRoute allowedRoles={['ADMIN']}>
              <EditProfile />
            </RoleRoute>
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.PROFILE_EDIT}
        element={
          <ProtectedRoute>
            <EditProfile />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.ATTENDANCE}
        element={
          <ProtectedRoute>
            <Attendance />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.MY_LEAVES}
        element={
          <ProtectedRoute>
            <MyLeaves />
          </ProtectedRoute>
        }
      />
      <Route
        path={ROUTES.MY_SALARY}
        element={
          <ProtectedRoute>
            <MySalary />
          </ProtectedRoute>
        }
      />

      {/* Root Redirect */}
      <Route
        path={ROUTES.HOME}
        element={
          isAuthenticated ? (
            <Navigate to={user?.role === 'ADMIN' ? ROUTES.ADMIN_DASHBOARD : ROUTES.EMPLOYEE_DASHBOARD} replace />
          ) : (
            <Navigate to={ROUTES.LOGIN} replace />
          )
        }
      />

      {/* 404 Not Found */}
      <Route path={ROUTES.NOT_FOUND} element={<NotFound />} />
    </Routes>
  );
};
