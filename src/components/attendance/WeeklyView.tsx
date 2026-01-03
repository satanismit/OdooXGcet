/**
 * Weekly View Component
 * Displays weekly attendance summary
 */

import React from 'react';
import { WeeklyAttendance } from '../../types/attendance';
import { formatDate } from '../../utils/helpers';

interface WeeklyViewProps {
  weeklyData: WeeklyAttendance | null;
}

export const WeeklyView: React.FC<WeeklyViewProps> = ({ weeklyData }) => {
  if (!weeklyData) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6 text-center text-gray-500">
        No weekly data available
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">
        Weekly Summary ({formatDate(weeklyData.weekStart)} - {formatDate(weeklyData.weekEnd)})
      </h3>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Total Work Hours</p>
          <p className="text-2xl font-bold text-blue-700">
            {weeklyData.totalWorkHours.toFixed(1)} hrs
          </p>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <p className="text-sm text-gray-600">Present Days</p>
          <p className="text-2xl font-bold text-green-700">
            {weeklyData.presentDays} days
          </p>
        </div>
      </div>

      <div className="mt-4">
        <p className="text-sm text-gray-600">
          Average: {(weeklyData.totalWorkHours / weeklyData.presentDays || 0).toFixed(1)} hrs/day
        </p>
      </div>
    </div>
  );
};
