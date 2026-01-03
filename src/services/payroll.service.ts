/**
 * Payroll Service
 * Mock payroll service with dummy data
 */

import { PayrollRecord, SalaryInfo, SalaryBreakdown } from '../types/payroll';
import { mockApiCall } from './api';

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
  const records = MOCK_PAYROLL.filter(p => p.userId === userId);
  return mockApiCall(records);
};

/**
 * Get all payroll records (Admin only)
 */
export const getAllPayrollRecords = async (): Promise<PayrollRecord[]> => {
  return mockApiCall(MOCK_PAYROLL);
};

/**
 * Get salary information for a user
 */
export const getSalaryInfo = async (userId: string): Promise<SalaryInfo> => {
  const salaryInfo = MOCK_SALARY_INFO[userId] || {
    userId,
    currentSalary: {
      basicSalary: 40000,
      houseRent: 12000,
      transportAllowance: 4000,
      medicalAllowance: 2000,
      bonus: 0,
      deductions: 4000,
    },
    annualSalary: 648000,
    lastIncrement: '2025-01-01',
    nextReview: '2026-01-01',
  };
  
  return mockApiCall(salaryInfo);
};

/**
 * Update salary (Admin only)
 */
export const updateSalary = async (
  userId: string,
  salaryBreakdown: SalaryBreakdown
): Promise<SalaryInfo> => {
  const grossSalary = 
    salaryBreakdown.basicSalary +
    salaryBreakdown.houseRent +
    salaryBreakdown.transportAllowance +
    salaryBreakdown.medicalAllowance +
    salaryBreakdown.bonus;
  
  const netSalary = grossSalary - salaryBreakdown.deductions;
  
  const updatedInfo: SalaryInfo = {
    userId,
    currentSalary: salaryBreakdown,
    annualSalary: netSalary * 12,
    lastIncrement: new Date().toISOString().split('T')[0],
    nextReview: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  };
  
  MOCK_SALARY_INFO[userId] = updatedInfo;
  return mockApiCall(updatedInfo);
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
  const salaryInfo = await getSalaryInfo(userId);
  
  const grossSalary = 
    salaryInfo.currentSalary.basicSalary +
    salaryInfo.currentSalary.houseRent +
    salaryInfo.currentSalary.transportAllowance +
    salaryInfo.currentSalary.medicalAllowance +
    salaryInfo.currentSalary.bonus;
  
  const netSalary = grossSalary - salaryInfo.currentSalary.deductions;
  
  const newPayroll: PayrollRecord = {
    id: `${Date.now()}`,
    userId,
    userName,
    month,
    year,
    salaryBreakdown: salaryInfo.currentSalary,
    grossSalary,
    netSalary,
    paymentDate: new Date().toISOString().split('T')[0],
    status: 'PROCESSING',
  };
  
  MOCK_PAYROLL.push(newPayroll);
  return mockApiCall(newPayroll);
};
