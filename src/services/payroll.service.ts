/**
 * Payroll Service
 * Mock payroll service with dummy data
 */

import { PayrollRecord, SalaryInfo, SalaryBreakdown } from '../types/payroll';
import api from './api';

// Mock payroll data
const MOCK_PAYROLL: PayrollRecord[] = [
  {
    id: '1',
    userId: '2',
    userName: 'John Doe',
    month: 'December',
    year: 2025,
    salaryBreakdown: {
      basicSalary: 50000,
      houseRent: 15000,
      transportAllowance: 5000,
      medicalAllowance: 3000,
      bonus: 2000,
      deductions: 5000,
    },
    grossSalary: 75000,
    netSalary: 70000,
    paymentDate: '2025-12-31',
    status: 'PAID',
  },
];

const MOCK_SALARY_INFO: { [userId: string]: SalaryInfo } = {
  '2': {
    userId: '2',
    currentSalary: {
      basicSalary: 50000,
      houseRent: 15000,
      transportAllowance: 5000,
      medicalAllowance: 3000,
      bonus: 2000,
      deductions: 5000,
    },
    annualSalary: 840000, // Net salary * 12
    lastIncrement: '2025-07-01',
    nextReview: '2026-07-01',
  },
};

/**
 * Get payroll records for a user
 */
export const getPayrollRecords = async (userId: string): Promise<PayrollRecord[]> => {
  const response = await api.get(`/payroll/user/${userId}`);
  return response.data;
};

/**
 * Get all payroll records (Admin only)
 */
export const getAllPayrollRecords = async (): Promise<PayrollRecord[]> => {
  const response = await api.get('/payroll/all');
  return response.data;
};

/**
 * Get salary information for a user
 */
export const getSalaryInfo = async (userId: string): Promise<SalaryInfo> => {
  const response = await api.get(`/salary/${userId}`);
  return response.data;
};

/**
 * Update salary (Admin only)
 */
export const updateSalary = async (
  userId: string,
  salaryBreakdown: SalaryBreakdown
): Promise<SalaryInfo> => {
  const response = await api.put(`/salary/${userId}`, salaryBreakdown);
  return response.data;
};

/**
 * Generate payroll for a month (Admin only)
 */
export const generatePayroll = async (
  userId: string,
  userName: string,
  month: string,
  year: number
): Promise<PayrollRecord> => {
  const response = await api.post('/payroll/generate', {
    user_id: userId,
    month: `${month}-${year}`,
  });
  return response.data;
};
