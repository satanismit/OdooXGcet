import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User } from '../../types/user';
import * as authService from '../../services/auth.service';
import * as attendanceService from '../../services/attendance.service';
import { getInitials } from '../../utils/helpers';

interface EmployeeGridProps {
  isAdmin?: boolean;
}

export const EmployeeGrid: React.FC<EmployeeGridProps> = ({ isAdmin = false }) => {
  const navigate = useNavigate();
  const [users, setUsers] = useState<User[]>([]);
  const [attendanceStatus, setAttendanceStatus] = useState<Record<string, 'PRESENT' | 'ABSENT'>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [usersData, statusData] = await Promise.all([
        authService.getAllUsers(),
        attendanceService.getAllAttendanceStatus(),
      ]);
      setUsers(usersData);
      setAttendanceStatus(statusData);
    } catch (error) {
      console.error('Failed to load employee data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCardClick = (userId: string) => {
    // Navigate to profile view
    // We need to update the route to support /profile/:id or use a modal
    // For now, let's assume we'll implement the route change next
    navigate(`/profile/${userId}`);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {users.map((user) => (
        <div
          key={user.id}
          onClick={() => handleCardClick(user.id)}
          className="bg-white rounded-lg shadow-md overflow-hidden cursor-pointer hover:shadow-lg transition-shadow relative group"
        >
          {/* Status Indicator */}
          <div className="absolute top-3 right-3 z-10">
            <div
              className={`w-4 h-4 rounded-full border-2 border-white shadow-sm ${
                attendanceStatus[user.id] === 'PRESENT' ? 'bg-green-500' : 'bg-red-500'
              }`}
              title={attendanceStatus[user.id] === 'PRESENT' ? 'Present' : 'Absent'}
            />
          </div>

          <div className="p-6 flex flex-col items-center text-center">
            {/* Avatar */}
            <div className="w-24 h-24 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-2xl font-bold mb-4 shadow-inner">
              {user.avatar ? (
                <img src={user.avatar} alt={user.firstName} className="w-full h-full rounded-full object-cover" />
              ) : (
                getInitials(user.firstName, user.lastName)
              )}
            </div>

            {/* Info */}
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {user.firstName} {user.lastName}
            </h3>
            <p className="text-sm text-primary-600 font-medium mb-1">{user.position}</p>
            <p className="text-xs text-gray-500">{user.department}</p>

            {/* Admin Actions (if needed) */}
            {isAdmin && (
              <div className="mt-4 pt-4 border-t border-gray-100 w-full opacity-0 group-hover:opacity-100 transition-opacity">
                <span className="text-xs text-primary-600 font-medium">Click to manage</span>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
