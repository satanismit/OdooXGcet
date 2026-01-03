/**
 * Leave Type Definitions
 * Defines leave types, status, and leave request structure
 */

export type LeaveType = 'PAID' | 'SICK' | 'UNPAID' | 'CASUAL';
export type LeaveStatus = 'PENDING' | 'APPROVED' | 'REJECTED';

export interface LeaveRequest {
  id: string;
  userId: string;
  userName: string;
  leaveType: LeaveType;
  startDate: string;
  endDate: string;
  reason: string;
  status: LeaveStatus;
  appliedOn: string;
  approvedBy?: string;
  approvedOn?: string;
  rejectionReason?: string;
  totalDays: number;
}

export interface LeaveBalance {
  userId: string;
  paidLeave: number;
  sickLeave: number;
  casualLeave: number;
  totalUsed: number;
}

export interface LeaveStats {
  totalPending: number;
  totalApproved: number;
  totalRejected: number;
}
