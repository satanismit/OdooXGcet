/**
 * Authentication Service
 * Real backend integration with FastAPI
 */

import { AuthUser, LoginCredentials, RegisterData, User } from '../types/user';
import api, { setAuthToken, removeAuthToken, handleApiError } from './api';
import { STORAGE_KEYS } from '../utils/constants';

// ========================================
// AUTHENTICATION FUNCTIONS
// ========================================

/**
 * Login user with backend API
 */
export const login = async (credentials: LoginCredentials): Promise<AuthUser> => {
  try {
    console.log('🔐 Logging in:', credentials.email);
    console.log('📤 Sending login request to:', '/auth/login');
    console.log('📦 Request data:', { login_id_or_email: credentials.email, password: '[HIDDEN]' });
    
    const response = await api.post('/auth/login', {
      login_id_or_email: credentials.email,
      password: credentials.password,
    });

    const { access_token, user } = response.data;
    
    // Save token to localStorage
    setAuthToken(access_token);
    
    // Save user data
    localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(user));
    
    console.log('✅ Login successful:', user.name);
    
    return {
      user: {
        id: user.login_id,
        email: user.login_id,
        firstName: user.name.split(' ')[0],
        lastName: user.name.split(' ').slice(1).join(' '),
        role: user.role,
        department: 'Engineering', // You can fetch this from profile later
        position: 'Employee',
        joinDate: user.joining_date,
        phone: '',
        address: '',
        dob: '',
        nationality: 'Indian',
        personalEmail: user.login_id,
        gender: 'Male',
        maritalStatus: 'Single',
        bankName: '',
        accountNumber: '',
        ifscCode: '',
        panNo: '',
      },
      token: access_token,
    };
  } catch (error) {
    console.error('❌ Login failed:', error);
    console.error('❌ Error details:', error instanceof Error ? error.message : 'Unknown error');
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as any;
      console.error('❌ Response status:', axiosError.response?.status);
      console.error('❌ Response data:', axiosError.response?.data);
    }
    throw new Error(handleApiError(error));
  }
};

/**
 * Register new user (Admin creates employee)
 */
export const register = async (data: RegisterData): Promise<AuthUser> => {
  try {
    console.log('📝 Registering user:', data.email);
    
    const response = await api.post('/admin/create-employee', {
      first_name: data.firstName,
      last_name: data.lastName,
      email: data.email,
      joining_date: new Date().toISOString(),
    });

    const { login_id, password } = response.data;
    
    console.log('✅ Registration successful. Login ID:', login_id);
    
    // Return the credentials for display
    return {
      user: {
        id: login_id,
        email: data.email,
        firstName: data.firstName,
        lastName: data.lastName,
        role: 'EMPLOYEE',
        department: data.department || 'Engineering',
        position: data.position || 'Employee',
        joinDate: new Date().toISOString().split('T')[0],
        phone: data.phone || '',
        address: '',
        dob: '',
        nationality: 'Indian',
        personalEmail: data.email,
        gender: 'Male',
        maritalStatus: 'Single',
        bankName: '',
        accountNumber: '',
        ifscCode: '',
        panNo: '',
      },
      token: password, // Temp password returned
    };
  } catch (error) {
    console.error('❌ Registration failed:', error);
    throw new Error(handleApiError(error));
  }
};

/**
 * Logout user
 */
export const logout = (): void => {
  console.log('👋 Logging out...');
  removeAuthToken();
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
  return !!localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
};

/**
 * Get user profile from backend
 */
export const getUserProfile = async (): Promise<User> => {
  try {
    const response = await api.get('/auth/users/me');
    const profile = response.data;
    
    return {
      id: profile.login_id || profile.user_id,
      email: profile.login_id,
      firstName: profile.name?.split(' ')[0] || '',
      lastName: profile.name?.split(' ').slice(1).join(' ') || '',
      role: profile.role,
      department: 'Engineering',
      position: 'Employee',
      joinDate: profile.joining_date,
      phone: profile.phone || '',
      address: profile.address || '',
      dob: profile.date_of_birth || '',
      nationality: 'Indian',
      personalEmail: profile.login_id,
      gender: profile.gender || 'Male',
      maritalStatus: 'Single',
      bankName: profile.bank_name || '',
      accountNumber: profile.account_number || '',
      ifscCode: profile.ifsc_code || '',
      panNo: profile.pan_number || '',
    };
  } catch (error) {
    console.error('❌ Failed to fetch profile:', error);
    throw new Error(handleApiError(error));
  }
};

/**
 * Update user profile
 */
export const updateUser = async (data: Partial<User>): Promise<User> => {
  try {
    // Update personal details
    if (data.firstName || data.lastName || data.phone || data.address || data.dob) {
      await api.put('/profile/personal', {
        father_name: '',
        mother_name: '',
        date_of_birth: data.dob,
        gender: data.gender,
        phone: data.phone,
        address: data.address,
        pan_number: data.panNo,
      });
    }
    
    // Update bank details
    if (data.bankName || data.accountNumber || data.ifscCode) {
      await api.put('/profile/bank', {
        bank_name: data.bankName,
        account_number: data.accountNumber,
        ifsc_code: data.ifscCode,
        branch_name: '',
      });
    }
    
    // Fetch updated profile
    return await getUserProfile();
  } catch (error) {
    console.error('❌ Failed to update profile:', error);
    throw new Error(handleApiError(error));
  }
};

/**
 * Get all users (for admin dashboard)
 */
export const getAllUsers = async (): Promise<User[]> => {
  try {
    const response = await api.get('/dashboard/employees');
    const employees = response.data;
    
    // Map response to User type
    if (Array.isArray(employees)) {
      return employees.map((emp: any) => ({
        id: emp.login_id || emp.id,
        email: emp.email || emp.login_id,
        firstName: emp.first_name || '',
        lastName: emp.last_name || '',
        role: emp.role || 'EMPLOYEE',
        department: emp.department || 'Engineering',
        position: emp.position || 'Employee',
        joinDate: emp.joining_date || new Date().toISOString(),
        phone: emp.phone || '',
        address: emp.address || '',
        dob: emp.date_of_birth || '',
        nationality: 'Indian',
        personalEmail: emp.email || emp.login_id,
        gender: emp.gender || 'Male',
        maritalStatus: 'Single',
        bankName: emp.bank_name || '',
        accountNumber: emp.account_number || '',
        ifscCode: emp.ifsc_code || '',
        panNo: emp.pan_number || '',
      }));
    }
    return [];
  } catch (error) {
    console.error('❌ Failed to fetch all users:', error);
    return [];
  }
};


