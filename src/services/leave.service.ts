/**
 * Leave Service
 * Mock leave management service with dummy data
 */

import { LeaveRequest, LeaveBalance, LeaveStats, LeaveType, LeaveStatus } from '../types/leave';
import { mockApiCall } from './api';
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
  const leaves = MOCK_LEAVES.filter(l => l.userId === userId);
  return mockApiCall(leaves);
};

/**
 * Get all leave requests (Admin only)
 */
export const getAllLeaveRequests = async (): Promise<LeaveRequest[]> => {
  return mockApiCall(MOCK_LEAVES);
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
  const totalDays = calculateDaysBetween(startDate, endDate);
  
  const newLeave: LeaveRequest = {
    id: `${Date.now()}`,
    userId,
    userName,
    leaveType,
    startDate,
    endDate,
    reason,
    status: 'PENDING',
    appliedOn: new Date().toISOString().split('T')[0],
    totalDays,
  };
  
  MOCK_LEAVES.push(newLeave);
  return mockApiCall(newLeave);
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
  const leaveIndex = MOCK_LEAVES.findIndex(l => l.id === leaveId);
  
  if (leaveIndex === -1) {
    throw new Error('Leave request not found');
  }
  
  const leave = MOCK_LEAVES[leaveIndex];
  leave.status = status;
  leave.approvedBy = approvedBy;
  leave.approvedOn = new Date().toISOString().split('T')[0];
  
  if (status === 'REJECTED' && rejectionReason) {
    leave.rejectionReason = rejectionReason;
  }
  
  return mockApiCall(leave);
};

/**
 * Get leave balance for a user
 */
export const getLeaveBalance = async (userId: string): Promise<LeaveBalance> => {
  const userLeaves = MOCK_LEAVES.filter(l => l.userId === userId && l.status === 'APPROVED');
  
  const usedPaid = userLeaves.filter(l => l.leaveType === 'PAID').reduce((sum, l) => sum + l.totalDays, 0);
  const usedSick = userLeaves.filter(l => l.leaveType === 'SICK').reduce((sum, l) => sum + l.totalDays, 0);
  const usedCasual = userLeaves.filter(l => l.leaveType === 'CASUAL').reduce((sum, l) => sum + l.totalDays, 0);
  
  const balance: LeaveBalance = {
    userId,
    paidLeave: DEFAULT_LEAVE_BALANCE.PAID - usedPaid,
    sickLeave: DEFAULT_LEAVE_BALANCE.SICK - usedSick,
    casualLeave: DEFAULT_LEAVE_BALANCE.CASUAL - usedCasual,
    totalUsed: usedPaid + usedSick + usedCasual,
  };
  
  return mockApiCall(balance);
};

/**
 * Get leave statistics (Admin only)
 */
export const getLeaveStats = async (): Promise<LeaveStats> => {
  const stats: LeaveStats = {
    totalPending: MOCK_LEAVES.filter(l => l.status === 'PENDING').length,
    totalApproved: MOCK_LEAVES.filter(l => l.status === 'APPROVED').length,
    totalRejected: MOCK_LEAVES.filter(l => l.status === 'REJECTED').length,
  };
  
  return mockApiCall(stats);
};

/**
 * Cancel leave request
 */
export const cancelLeave = async (leaveId: string): Promise<void> => {
  const leaveIndex = MOCK_LEAVES.findIndex(l => l.id === leaveId);
  
  if (leaveIndex === -1) {
    throw new Error('Leave request not found');
  }
  
  if (MOCK_LEAVES[leaveIndex].status !== 'PENDING') {
    throw new Error('Can only cancel pending leave requests');
  }
  
  MOCK_LEAVES.splice(leaveIndex, 1);
  return mockApiCall(undefined);
};
