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
            <h1 className="text-2xl font-bold text-gray-800">
              {getGreeting()}, {user?.firstName}!
            </h1>
            <p className="text-gray-600">Admin Dashboard - Manage your team</p>
          </div>
        </div>

        {/* Employee Grid */}
        <EmployeeGrid isAdmin={true} />
      </div>
    </Layout>
  );
};
