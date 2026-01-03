/**
 * Payroll Type Definitions
 * Defines salary structure and payroll records
 */

export interface SalaryBreakdown {
  basicSalary: number;
  houseRent: number;
  transportAllowance: number;
  medicalAllowance: number;
  bonus: number;
  deductions: number;
}

export interface PayrollRecord {
  id: string;
  userId: string;
  userName: string;
  month: string;
  year: number;
  salaryBreakdown: SalaryBreakdown;
  grossSalary: number;
  netSalary: number;
  paymentDate: string;
  status: 'PENDING' | 'PAID' | 'PROCESSING';
}

export interface SalaryInfo {
  userId: string;
  currentSalary: SalaryBreakdown;
  annualSalary: number;
  lastIncrement: string;
  nextReview: string;
}
