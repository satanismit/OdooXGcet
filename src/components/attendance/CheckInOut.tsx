/**
 * Check In/Out Component
 * Handles daily attendance check-in and check-out
 */

import React, { useState, useEffect } from 'react';
import { Button } from '../common/Button';
import { useAuth } from '../../context/AuthContext';
import * as attendanceService from '../../services/attendance.service';
import { AttendanceRecord } from '../../types/attendance';
import { formatTime } from '../../utils/helpers';

export const CheckInOut: React.FC = () => {
  const { user } = useAuth();
  const [todayRecord, setTodayRecord] = useState<AttendanceRecord | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadTodayAttendance();
  }, []);

  const loadTodayAttendance = async () => {
    if (!user) return;
    try {
      const record = await attendanceService.getTodayAttendance(user.id);
      setTodayRecord(record);
    } catch (err) {
      console.error('Failed to load attendance:', err);
    }
  };

  const handleCheckIn = async () => {
    if (!user) return;
    setLoading(true);
    setError('');
    try {
      const record = await attendanceService.checkIn(user.id);
      setTodayRecord(record);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCheckOut = async () => {
    if (!user) return;
    setLoading(true);
    setError('');
    try {
      const record = await attendanceService.checkOut(user.id);
      setTodayRecord(record);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-4">Today's Attendance</h2>
      
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
          {error}
        </div>
      )}

      <div className="space-y-4">
        {todayRecord ? (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Check In</p>
                <p className="text-lg font-semibold text-green-700">
                  {todayRecord.checkIn ? formatTime(todayRecord.checkIn) : 'Not checked in'}
                </p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Check Out</p>
                <p className="text-lg font-semibold text-blue-700">
                  {todayRecord.checkOut ? formatTime(todayRecord.checkOut) : 'Not checked out'}
                </p>
              </div>
            </div>

            {todayRecord.checkOut && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">Total Work Hours</p>
                <p className="text-lg font-semibold text-gray-800">
                  {todayRecord.workHours.toFixed(2)} hours
                </p>
              </div>
            )}

            {!todayRecord.checkOut && (
              <Button
                onClick={handleCheckOut}
                isLoading={loading}
                variant="danger"
                fullWidth
              >
                Check Out
              </Button>
            )}
          </>
        ) : (
          <Button
            onClick={handleCheckIn}
            isLoading={loading}
            variant="success"
            fullWidth
          >
            Check In
          </Button>
        )}
      </div>
    </div>
  );
};
