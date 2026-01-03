/**
 * User Type Definitions
 * Defines user roles and user data structure
 */

export type UserRole = 'EMPLOYEE' | 'ADMIN';

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  department: string;
  position: string;
  joinDate: string;
  phone: string;
  address: string;
  avatar?: string;
  
  // Extended Profile Info
  dob?: string;
  nationality?: string;
  personalEmail?: string;
  gender?: 'Male' | 'Female' | 'Other';
  maritalStatus?: 'Single' | 'Married' | 'Divorced' | 'Widowed';
  
  // Bank Info
  bankName?: string;
  accountNumber?: string;
  ifscCode?: string;
  panNo?: string;
}

export interface AuthUser {
  user: User;
  token: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  department: string;
  position: string;
  phone: string;
}
