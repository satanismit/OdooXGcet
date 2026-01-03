/**
 * Attendance Service
 * Mock attendance service with dummy data
 */

import { AttendanceRecord, AttendanceStats, WeeklyAttendance } from '../types/attendance';
import api from './api';
import { calculateWorkHours } from '../utils/helpers';

// Mock attendance data
let MOCK_ATTENDANCE: AttendanceRecord[] = [
  {
    id: '1',
    userId: '2',
    date: '2026-01-01',
    checkIn: '2026-01-01T09:00:00',
    checkOut: '2026-01-01T18:00:00',
    status: 'PRESENT',
    workHours: 9,
  },
  {
    id: '2',
    userId: '2',
    date: '2026-01-02',
    checkIn: '2026-01-02T09:15:00',
    checkOut: '2026-01-02T18:30:00',
    status: 'PRESENT',
    workHours: 9.25,
  },
];

/**
 * Get attendance records for a user
 */
export const getAttendanceRecords = async (userId: string): Promise<AttendanceRecord[]> => {
  const response = await api.get(`/attendance/records/${userId}`);
  return response.data;
};

/**
 * Check in
 */
export const checkIn = async (userId: string): Promise<AttendanceRecord> => {
  const response = await api.post('/attendance/check-in');
  return response.data;
};

/**
 * Check out
 */
export const checkOut = async (userId: string): Promise<AttendanceRecord> => {
  const response = await api.post('/attendance/check-out');
  return response.data;
};

/**
 * Get today's attendance
 */
export const getTodayAttendance = async (userId: string): Promise<AttendanceRecord | null> => {
  try {
    const response = await api.get('/attendance/today');
    return response.data;
  } catch (error) {
    return null;
  }
};

/**
 * Get attendance status for all users (for directory view)
 */
export const getAllAttendanceStatus = async (): Promise<Record<string, 'PRESENT' | 'ABSENT'>> => {
  const response = await api.get('/dashboard/employees');
  return response.data;
};

/**
 * Get weekly attendance
 */
export const getWeeklyAttendance = async (userId: string): Promise<WeeklyAttendance> => {
  const response = await api.get(`/attendance/weekly/${userId}`);
  return response.data;
};

/**
 * Get attendance statistics
 */
export const getAttendanceStats = async (userId: string): Promise<AttendanceStats> => {
  const response = await api.get(`/attendance/stats/${userId}`);
  return response.data;
};
