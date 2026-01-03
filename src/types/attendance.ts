/**
 * Attendance Type Definitions
 * Defines attendance status and record structure
 */

export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'LEAVE';

export interface AttendanceRecord {
  id: string;
  userId: string;
  date: string;
  checkIn: string | null;
  checkOut: string | null;
  status: AttendanceStatus;
  workHours: number;
  notes?: string;
}

export interface WeeklyAttendance {
  weekStart: string;
  weekEnd: string;
  records: AttendanceRecord[];
  totalWorkHours: number;
  presentDays: number;
}

export interface AttendanceStats {
  totalPresent: number;
  totalAbsent: number;
  totalHalfDay: number;
  totalLeave: number;
  averageWorkHours: number;
}
