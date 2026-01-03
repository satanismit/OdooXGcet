/**
 * Leave Service
 * Mock leave management service with dummy data
 */

import { LeaveRequest, LeaveBalance, LeaveStats, LeaveType, LeaveStatus } from '../types/leave';
import api from './api';
import { calculateDaysBetween } from '../utils/helpers';
import { DEFAULT_LEAVE_BALANCE } from '../utils/constants';

// Mock leave data
let MOCK_LEAVES: LeaveRequest[] = [
  {
    id: '1',
    userId: '2',
    userName: 'John Doe',
    leaveType: 'PAID',
    startDate: '2025-12-20',
    endDate: '2025-12-22',
    reason: 'Family vacation',
    status: 'APPROVED',
    appliedOn: '2025-12-10',
    approvedBy: 'Admin User',
    approvedOn: '2025-12-11',
    totalDays: 3,
  },
];

/**
 * Get leave requests for a user
 */
export const getLeaveRequests = async (userId: string): Promise<LeaveRequest[]> => {
  const response = await api.get(`/leaves/my-leaves`);
  return response.data;
};

/**
 * Get all leave requests (Admin only)
 */
export const getAllLeaveRequests = async (): Promise<LeaveRequest[]> => {
  const response = await api.get('/leaves/admin/pending');
  return response.data;
};

/**
 * Apply for leave
 */
export const applyLeave = async (
  userId: string,
  userName: string,
  leaveType: LeaveType,
  startDate: string,
  endDate: string,
  reason: string
): Promise<LeaveRequest> => {
  const response = await api.post('/leaves/apply', {
    start_date: startDate,
    end_date: endDate,
    leave_type: leaveType,
    reason,
  });
  return response.data;
};

/**
 * Update leave status (Admin only)
 */
export const updateLeaveStatus = async (
  leaveId: string,
  status: LeaveStatus,
  approvedBy: string,
  rejectionReason?: string
): Promise<LeaveRequest> => {
  const response = await api.put(`/leaves/admin/action/${leaveId}`, {
    action: status.toLowerCase(),
    admin_comment: rejectionReason
  });
  return response.data;
};

/**
 * Get leave balance for a user
 */
export const getLeaveBalance = async (userId: string): Promise<LeaveBalance> => {
  const response = await api.get('/leaves/me/balance');
  return response.data;
};

/**
 * Get leave statistics (Admin only)
 */
export const getLeaveStats = async (): Promise<LeaveStats> => {
  // Mock implementation - can be replaced with actual API call when endpoint exists
  return {
    totalLeaves: 10,
    pendingLeaves: 2,
    approvedLeaves: 6,
    rejectedLeaves: 2
  };
};

/**
 * Cancel leave request
 */
export const cancelLeave = async (leaveId: string): Promise<void> => {
  // Mock implementation - delete functionality not available in current API
  console.warn('Delete leave functionality not implemented in backend');
  throw new Error('Delete leave functionality not available');
};
