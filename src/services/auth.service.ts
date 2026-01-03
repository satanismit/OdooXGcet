/**
 * Authentication Service
 * Mock authentication service with dummy data
 */

import { AuthUser, LoginCredentials, RegisterData, User } from '../types/user';
import { mockApiCall, mockApiError } from './api';
import { STORAGE_KEYS } from '../utils/constants';

// Mock user database
const MOCK_USERS: User[] = [
  {
    id: '1',
    email: 'admin@dayflow.com',
    firstName: 'Admin',
    lastName: 'User',
    role: 'ADMIN',
    department: 'Management',
    position: 'HR Manager',
    joinDate: '2023-01-01',
    phone: '+91 98765 43210',
    address: '123 Business Park, Mumbai, India',
    dob: '1985-05-15',
    nationality: 'Indian',
    personalEmail: 'admin.personal@gmail.com',
    gender: 'Male',
    maritalStatus: 'Married',
    bankName: 'HDFC Bank',
    accountNumber: '123456789012',
    ifscCode: 'HDFC0001234',
    panNo: 'ABCDE1234F',
  },
  {
    id: '2',
    email: 'employee@dayflow.com',
    firstName: 'John',
    lastName: 'Doe',
    role: 'EMPLOYEE',
    department: 'Engineering',
    position: 'Software Developer',
    joinDate: '2023-06-15',
    phone: '+91 98765 43211',
    address: '456 Tech Avenue, Bangalore, India',
    dob: '1995-08-20',
    nationality: 'Indian',
    personalEmail: 'john.doe@gmail.com',
    gender: 'Male',
    maritalStatus: 'Single',
    bankName: 'ICICI Bank',
    accountNumber: '987654321098',
    ifscCode: 'ICIC0005678',
    panNo: 'FGHIJ5678K',
  },
];

/**
 * Login user
 */
export const login = async (credentials: LoginCredentials): Promise<AuthUser> => {
  const user = MOCK_USERS.find(u => u.email === credentials.email);
  
  if (!user) {
    return mockApiError('Invalid email or password');
  }
  
  // Mock password check (any password works in demo)
  if (!credentials.password) {
    return mockApiError('Password is required');
  }
  
  const authUser: AuthUser = {
    user,
    token: `mock-token-${user.id}-${Date.now()}`,
  };
  
  // Store in localStorage
  localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, authUser.token);
  localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(authUser.user));
  
  return mockApiCall(authUser);
};

/**
 * Register new user
 */
export const register = async (data: RegisterData): Promise<AuthUser> => {
  // Check if email already exists
  const existingUser = MOCK_USERS.find(u => u.email === data.email);
  if (existingUser) {
    return mockApiError('Email already registered');
  }
  
  const newUser: User = {
    id: `${Date.now()}`,
    email: data.email,
    firstName: data.firstName,
    lastName: data.lastName,
    role: 'EMPLOYEE', // New users are always employees
    department: data.department,
    position: data.position,
    joinDate: new Date().toISOString().split('T')[0],
    phone: data.phone,
    address: '',
  };
  
  MOCK_USERS.push(newUser);
  
  const authUser: AuthUser = {
    user: newUser,
    token: `mock-token-${newUser.id}-${Date.now()}`,
  };
  
  // Store in localStorage
  localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, authUser.token);
  localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(authUser.user));
  
  return mockApiCall(authUser);
};

/**
 * Logout user
 */
export const logout = (): void => {
  localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
  localStorage.removeItem(STORAGE_KEYS.USER_DATA);
};

/**
 * Get current user from localStorage
 */
export const getCurrentUser = (): User | null => {
  const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
  if (userData) {
    return JSON.parse(userData);
  }
  return null;
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
  return !!token;
};

/**
 * Get all users (for directory view)
 */
export const getAllUsers = async (): Promise<User[]> => {
  return mockApiCall(MOCK_USERS);
};

/**
 * Get user by ID
 */
export const getUserById = async (id: string): Promise<User | null> => {
  const user = MOCK_USERS.find(u => u.id === id);
  return mockApiCall(user || null);
};

/**
 * Update user profile
 */
export const updateUser = async (data: Partial<User>): Promise<User> => {
  const currentUser = getCurrentUser();
  if (!currentUser) return mockApiError('User not found');
  
  return updateUserById(currentUser.id, data);
};

/**
 * Update user by ID (Admin function)
 */
export const updateUserById = async (id: string, data: Partial<User>): Promise<User> => {
  const index = MOCK_USERS.findIndex(u => u.id === id);
  if (index !== -1) {
    MOCK_USERS[index] = { ...MOCK_USERS[index], ...data };
    
    // If updating current user, update local storage
    const currentUser = getCurrentUser();
    if (currentUser && currentUser.id === id) {
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(MOCK_USERS[index]));
    }
    
    return mockApiCall(MOCK_USERS[index]);
  }
  
  return mockApiError('User not found');
};

