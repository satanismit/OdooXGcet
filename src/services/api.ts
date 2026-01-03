/**
 * API Client Configuration
 * Centralized Axios instance for all backend communication
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';

// ========================================
// API CONFIGURATION
// ========================================
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

console.log('🔗 API Base URL:', API_BASE_URL);

// Create Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 second timeout
});

// ========================================
// REQUEST INTERCEPTOR
// ========================================
// Automatically attach JWT token to every request
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('dayflow_auth_token');
    
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('🔐 Token attached to request:', config.url);
    }
    
    console.log('📤 API Request:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// ========================================
// RESPONSE INTERCEPTOR
// ========================================
// Handle errors and token expiration
api.interceptors.response.use(
  (response) => {
    console.log('📥 API Response:', response.config.url, response.status);
    return response;
  },
  (error: AxiosError) => {
    console.error('❌ API Error:', error.response?.status, error.config?.url);

    // Handle 401 Unauthorized (Token expired or invalid)
    if (error.response?.status === 401) {
      console.warn('⚠️ Session expired. Redirecting to login...');
      
      // Clear authentication data
      localStorage.removeItem('dayflow_auth_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('dayflow_user_data');
      
      // Redirect to login (only if not already on login page)
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }

    // Handle 403 Forbidden (Insufficient permissions)
    if (error.response?.status === 403) {
      console.error('🚫 Access Denied: Insufficient permissions');
    }

    // Handle 500 Server Error
    if (error.response?.status === 500) {
      console.error('💥 Server Error: Please try again later');
    }

    // Handle Network Error (Backend down)
    if (!error.response) {
      console.error('🌐 Network Error: Cannot connect to server');
      // You can show a toast notification here
      alert('Server is down. Please check if the backend is running on ' + API_BASE_URL);
    }

    return Promise.reject(error);
  }
);

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Set authentication token
 */
export const setAuthToken = (token: string) => {
  localStorage.setItem('dayflow_auth_token', token);
  console.log('✅ Token saved to localStorage');
};

/**
 * Get authentication token
 */
export const getAuthToken = () => {
  return localStorage.getItem('dayflow_auth_token');
};

/**
 * Remove authentication token
 */
export const removeAuthToken = () => {
  localStorage.removeItem('dayflow_auth_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('dayflow_user_data');
  console.log('🗑️ Tokens cleared from localStorage');
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
  return !!getAuthToken();
};

// ========================================
// API ERROR HANDLER
// ========================================
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{ detail: string }>;
    
    // Extract error message from response
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }
    
    // Handle different status codes
    switch (axiosError.response?.status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Session expired. Please login again.';
      case 403:
        return 'You do not have permission to perform this action.';
      case 404:
        return 'Resource not found.';
      case 500:
        return 'Server error. Please try again later.';
      default:
        return axiosError.message || 'An unexpected error occurred';
    }
  }
  
  return 'An unexpected error occurred';
};

// ========================================
// EXPORTS
// ========================================
export default api;

// Also export for named imports
export { api, API_BASE_URL };
