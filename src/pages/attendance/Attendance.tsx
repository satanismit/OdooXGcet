/**
 * Attendance Page
 * Employee attendance tracking page
 */

import React, { useEffect, useState } from 'react';
import { Layout } from '../../components/layout/Layout';
import { CheckInOut } from '../../components/attendance/CheckInOut';
import { AttendanceTable } from '../../components/attendance/AttendanceTable';
import { WeeklyView } from '../../components/attendance/WeeklyView';
import { useAuth } from '../../context/AuthContext';
import * as attendanceService from '../../services/attendance.service';
import { AttendanceRecord, WeeklyAttendance } from '../../types/attendance';

export const Attendance: React.FC = () => {
  const { user } = useAuth();
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [weeklyData, setWeeklyData] = useState<WeeklyAttendance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAttendanceData();
  }, []);

  const loadAttendanceData = async () => {
    if (!user) return;
    try {
      const [attendanceRecords, weekly] = await Promise.all([
        attendanceService.getAttendanceRecords(user.id),
        attendanceService.getWeeklyAttendance(user.id),
      ]);
      setRecords(attendanceRecords);
      setWeeklyData(weekly);
    } catch (err) {
      console.error('Failed to load attendance data:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">Attendance</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <CheckInOut />
          <WeeklyView weeklyData={weeklyData} />
        </div>

        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Attendance History</h2>
          <AttendanceTable records={records} />
        </div>
      </div>
    </Layout>
  );
};
