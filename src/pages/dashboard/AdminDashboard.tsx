/**
 * Admin Dashboard Page
 * Main dashboard for admin/HR users
 */

import React from 'react';
import { Layout } from '../../components/layout/Layout';
import { useAuth } from '../../context/AuthContext';
import { getGreeting } from '../../utils/helpers';
import { EmployeeGrid } from '../../components/dashboard/EmployeeGrid';

export const AdminDashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">
              {getGreeting()}, {user?.firstName || 'Admin'}!
            </h1>
            <p className="text-gray-600 mt-1">Admin Dashboard - Manage your team</p>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Total Employees</div>
            <div className="text-3xl font-bold text-primary-600 mt-2">12</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Present Today</div>
            <div className="text-3xl font-bold text-green-600 mt-2">10</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">On Leave</div>
            <div className="text-3xl font-bold text-orange-600 mt-2">2</div>
          </div>
        </div>

        {/* Employee Grid */}
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Employees</h2>
          <EmployeeGrid isAdmin={true} />
        </div>
      </div>
    </Layout>
  );
};
