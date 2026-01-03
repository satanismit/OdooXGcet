/**
 * Attendance Service
 * Mock attendance service with dummy data
 */

import { AttendanceRecord, AttendanceStats, WeeklyAttendance } from '../types/attendance';
import { mockApiCall } from './api';
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
  const records = MOCK_ATTENDANCE.filter(a => a.userId === userId);
  return mockApiCall(records);
};

/**
 * Check in
 */
export const checkIn = async (userId: string): Promise<AttendanceRecord> => {
  const today = new Date().toISOString().split('T')[0];
  const existingRecord = MOCK_ATTENDANCE.find(
    a => a.userId === userId && a.date === today
  );
  
  if (existingRecord && existingRecord.checkIn) {
    throw new Error('Already checked in today');
  }
  
  const now = new Date().toISOString();
  const newRecord: AttendanceRecord = {
    id: `${Date.now()}`,
    userId,
    date: today,
    checkIn: now,
    checkOut: null,
    status: 'PRESENT',
    workHours: 0,
  };
  
  MOCK_ATTENDANCE.push(newRecord);
  return mockApiCall(newRecord);
};

/**
 * Check out
 */
export const checkOut = async (userId: string): Promise<AttendanceRecord> => {
  const today = new Date().toISOString().split('T')[0];
  const recordIndex = MOCK_ATTENDANCE.findIndex(
    a => a.userId === userId && a.date === today
  );
  
  if (recordIndex === -1 || !MOCK_ATTENDANCE[recordIndex].checkIn) {
    throw new Error('No check-in record found for today');
  }
  
  if (MOCK_ATTENDANCE[recordIndex].checkOut) {
    throw new Error('Already checked out today');
  }
  
  const now = new Date().toISOString();
  const record = MOCK_ATTENDANCE[recordIndex];
  record.checkOut = now;
  record.workHours = calculateWorkHours(record.checkIn!, now);
  
  return mockApiCall(record);
};

/**
 * Get today's attendance
 */
export const getTodayAttendance = async (userId: string): Promise<AttendanceRecord | null> => {
  const today = new Date().toISOString().split('T')[0];
  const record = MOCK_ATTENDANCE.find(
    a => a.userId === userId && a.date === today
  );
  return mockApiCall(record || null);
};

/**
 * Get attendance status for all users (for directory view)
 */
export const getAllAttendanceStatus = async (): Promise<Record<string, 'PRESENT' | 'ABSENT'>> => {
  const today = new Date().toISOString().split('T')[0];
  const statusMap: Record<string, 'PRESENT' | 'ABSENT'> = {};
  
  // In a real app, we would fetch this from the backend
  // For mock, we'll check if they have a record for today
  MOCK_ATTENDANCE.forEach(record => {
    if (record.date === today && record.checkIn && !record.checkOut) {
      statusMap[record.userId] = 'PRESENT';
    }
  });
  
  return mockApiCall(statusMap);
};

/**
 * Get weekly attendance
 */
export const getWeeklyAttendance = async (userId: string): Promise<WeeklyAttendance> => {
  const records = MOCK_ATTENDANCE.filter(a => a.userId === userId).slice(-7);
  
  const weeklyData: WeeklyAttendance = {
    weekStart: records[0]?.date || '',
    weekEnd: records[records.length - 1]?.date || '',
    records,
    totalWorkHours: records.reduce((sum, r) => sum + r.workHours, 0),
    presentDays: records.filter(r => r.status === 'PRESENT').length,
  };
  
  return mockApiCall(weeklyData);
};

/**
 * Get attendance statistics
 */
export const getAttendanceStats = async (userId: string): Promise<AttendanceStats> => {
  const records = MOCK_ATTENDANCE.filter(a => a.userId === userId);
  
  const stats: AttendanceStats = {
    totalPresent: records.filter(r => r.status === 'PRESENT').length,
    totalAbsent: records.filter(r => r.status === 'ABSENT').length,
    totalHalfDay: records.filter(r => r.status === 'HALF_DAY').length,
    totalLeave: records.filter(r => r.status === 'LEAVE').length,
    averageWorkHours: records.reduce((sum, r) => sum + r.workHours, 0) / records.length || 0,
  };
  
  return mockApiCall(stats);
};
