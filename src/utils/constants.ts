/**
 * Application Constants
 * Central location for all app-wide constants
 */

export const APP_NAME = 'Dayflow';
export const APP_TAGLINE = 'Every workday, perfectly aligned';

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'dayflow_auth_token',
  USER_DATA: 'dayflow_user_data',
  THEME: 'dayflow_theme',
} as const;

// Routes
export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  VERIFY_EMAIL: '/verify-email',
  
  // Employee Routes
  EMPLOYEE_DASHBOARD: '/dashboard',
  PROFILE_VIEW: '/profile',
  PROFILE_EDIT: '/profile/edit',
  ATTENDANCE: '/attendance',
  MY_LEAVES: '/leaves',
  MY_SALARY: '/payroll',
  
  // Admin Routes
  ADMIN_DASHBOARD: '/admin/dashboard',
  LEAVE_APPROVALS: '/admin/leave-approvals',
  PAYROLL_ADMIN: '/admin/payroll',
  
  // Other
  NOT_FOUND: '*',
} as const;

// User Roles
export const ROLES = {
  EMPLOYEE: 'EMPLOYEE',
  ADMIN: 'ADMIN',
} as const;

// Attendance Status
export const ATTENDANCE_STATUS = {
  PRESENT: 'PRESENT',
  ABSENT: 'ABSENT',
  HALF_DAY: 'HALF_DAY',
  LEAVE: 'LEAVE',
} as const;

// Leave Types
export const LEAVE_TYPES = {
  PAID: 'PAID',
  SICK: 'SICK',
  UNPAID: 'UNPAID',
  CASUAL: 'CASUAL',
} as const;

// Leave Status
export const LEAVE_STATUS = {
  PENDING: 'PENDING',
  APPROVED: 'APPROVED',
  REJECTED: 'REJECTED',
} as const;

// Default Leave Balance (in days)
export const DEFAULT_LEAVE_BALANCE = {
  PAID: 20,
  SICK: 10,
  CASUAL: 7,
} as const;

// Work Hours
export const WORK_HOURS = {
  FULL_DAY: 8,
  HALF_DAY: 4,
} as const;

// Date Formats
export const DATE_FORMATS = {
  DISPLAY: 'DD/MM/YYYY',
  API: 'YYYY-MM-DD',
  DATETIME: 'DD/MM/YYYY HH:mm',
} as const;
