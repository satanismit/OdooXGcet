/**
 * My Leaves Page
 * Employee leave management page
 */

import React, { useEffect, useState } from 'react';
import { Layout } from '../../components/layout/Layout';
import { Button } from '../../components/common/Button';
import { ApplyLeaveForm } from '../../components/leave/ApplyLeaveForm';
import { LeaveTable } from '../../components/leave/LeaveTable';
import { useAuth } from '../../context/AuthContext';
import * as leaveService from '../../services/leave.service';
import { LeaveRequest, LeaveBalance } from '../../types/leave';

export const MyLeaves: React.FC = () => {
  const { user } = useAuth();
  const [leaves, setLeaves] = useState<LeaveRequest[]>([]);
  const [balance, setBalance] = useState<LeaveBalance | null>(null);
  const [showApplyForm, setShowApplyForm] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaveData();
  }, []);

  const loadLeaveData = async () => {
    if (!user) return;
    try {
      const [leaveRequests, leaveBalance] = await Promise.all([
        leaveService.getLeaveRequests(user.id),
        leaveService.getLeaveBalance(user.id),
      ]);
      setLeaves(leaveRequests);
      setBalance(leaveBalance);
    } catch (err) {
      console.error('Failed to load leave data:', err);
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
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">My Leaves</h1>
          <Button onClick={() => setShowApplyForm(true)}>
            Apply for Leave
          </Button>
        </div>

        {/* Leave Balance */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Leave Balance</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Paid Leave</p>
              <p className="text-2xl font-bold text-green-600">{balance?.paidLeave || 0} days</p>
            </div>
            <div className="bg-blue-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Sick Leave</p>
              <p className="text-2xl font-bold text-blue-600">{balance?.sickLeave || 0} days</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Casual Leave</p>
              <p className="text-2xl font-bold text-purple-600">{balance?.casualLeave || 0} days</p>
            </div>
            <div className="bg-red-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600">Total Used</p>
              <p className="text-2xl font-bold text-red-600">{balance?.totalUsed || 0} days</p>
            </div>
          </div>
        </div>

        {/* Leave Requests */}
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Leave Requests</h2>
          <LeaveTable leaves={leaves} />
        </div>
      </div>

      <ApplyLeaveForm
        isOpen={showApplyForm}
        onClose={() => setShowApplyForm(false)}
        onSuccess={loadLeaveData}
      />
    </Layout>
  );
};
