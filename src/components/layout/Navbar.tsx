/**
 * Navbar Component
 * Top navigation bar with user info and logout
 */

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { getInitials } from '../../utils/helpers';
import { APP_NAME, APP_TAGLINE, ROUTES } from '../../utils/constants';
import * as attendanceService from '../../services/attendance.service';

export const Navbar: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isCheckedIn, setIsCheckedIn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (user) {
      checkAttendanceStatus();
    }
    
    // Close dropdown when clicking outside
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [user]);

  const checkAttendanceStatus = async () => {
    if (!user || !user.id) return;
    try {
      const record = await attendanceService.getTodayAttendance(user.id);
      setIsCheckedIn(!!record && !!record.checkIn && !record.checkOut);
    } catch (error) {
      console.error('Failed to check attendance status', error);
    }
  };

  const handleAttendanceToggle = async () => {
    if (!user || !user.id) return;
    setLoading(true);
    try {
      if (isCheckedIn) {
        await attendanceService.checkOut(user.id);
        setIsCheckedIn(false);
      } else {
        await attendanceService.checkIn(user.id);
        setIsCheckedIn(true);
      }
      // Refresh page to update grid status if on dashboard
      if (window.location.pathname === ROUTES.EMPLOYEE_DASHBOARD || window.location.pathname === ROUTES.ADMIN_DASHBOARD) {
        window.location.reload();
      }
    } catch (error) {
      console.error('Attendance action failed', error);
      alert('Failed to update attendance. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-white shadow-md border-b border-gray-200 relative z-50">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/')}>
            <div className="flex-shrink-0">
              <h1 className="text-2xl font-bold text-primary-600">{APP_NAME}</h1>
              <p className="text-xs text-gray-500">{APP_TAGLINE}</p>
            </div>
          </div>

          {/* User Info */}
          {user && (
            <div className="flex items-center gap-6">
              {/* Attendance Systray */}
              <div className="hidden md:flex items-center gap-3 bg-gray-50 px-4 py-2 rounded-full border border-gray-200">
                <div className="flex flex-col items-end mr-2">
                  <span className="text-xs font-medium text-gray-500">Attendance</span>
                  <span className={`text-xs font-bold ${isCheckedIn ? 'text-green-600' : 'text-red-600'}`}>
                    {isCheckedIn ? 'CHECKED IN' : 'CHECKED OUT'}
                  </span>
                </div>
                <button
                  onClick={handleAttendanceToggle}
                  disabled={loading}
                  className={`px-4 py-1.5 rounded-full text-sm font-medium text-white transition-colors shadow-sm ${
                    isCheckedIn 
                      ? 'bg-red-500 hover:bg-red-600' 
                      : 'bg-green-500 hover:bg-green-600'
                  } ${loading ? 'opacity-70 cursor-not-allowed' : ''}`}
                >
                  {loading ? '...' : isCheckedIn ? 'Check Out ->' : 'Check In ->'}
                </button>
              </div>

              <div className="flex items-center gap-3 relative" ref={dropdownRef}>
                <div className="text-right hidden sm:block">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.firstName || 'User'} {user?.lastName || ''}
                  </p>
                  <p className="text-xs text-gray-500">{user?.role || 'Employee'}</p>
                </div>
                
                {/* Avatar */}
                <button 
                  onClick={() => setShowDropdown(!showDropdown)}
                  className="h-10 w-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold hover:ring-2 hover:ring-offset-2 hover:ring-primary-500 transition-all focus:outline-none"
                >
                  {getInitials(user?.firstName, user?.lastName)}
                </button>

                {/* Dropdown Menu */}
                {showDropdown && (
                  <div className="absolute right-0 top-12 w-48 bg-white rounded-md shadow-lg py-1 border border-gray-100 ring-1 ring-black ring-opacity-5 transform origin-top-right transition-all">
                    <Link
                      to={ROUTES.PROFILE_VIEW}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      onClick={() => setShowDropdown(false)}
                    >
                      My Profile
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      Log Out
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};
