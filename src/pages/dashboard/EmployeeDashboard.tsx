/**
 * Employee Dashboard Page
 * Main dashboard for employee users
 */

import React from 'react';
import { Layout } from '../../components/layout/Layout';
import { useAuth } from '../../context/AuthContext';
import { getGreeting } from '../../utils/helpers';
import { EmployeeGrid } from '../../components/dashboard/EmployeeGrid';

export const EmployeeDashboard: React.FC = () => {
  const { user } = useAuth();

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800">
              {getGreeting()}, {user?.firstName || 'User'}!
            </h1>
            <p className="text-gray-600 mt-1">Team Directory</p>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Your Department</div>
            <div className="text-2xl font-bold text-primary-600 mt-2">{user?.department || 'Engineering'}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-sm text-gray-600">Your Position</div>
            <div className="text-2xl font-bold text-primary-600 mt-2">{user?.position || 'Employee'}</div>
          </div>
        </div>

        {/* Employee Grid */}
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">Team Members</h2>
          <EmployeeGrid isAdmin={false} />
        </div>
      </div>
    </Layout>
  );
};
