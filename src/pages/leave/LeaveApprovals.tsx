/**
 * Leave Approvals Page
 * Admin page for approving/rejecting leave requests
 */

import React, { useEffect, useState } from 'react';
import { Layout } from '../../components/layout/Layout';
import { LeaveApprovalCard } from '../../components/leave/LeaveApprovalCard';
import * as leaveService from '../../services/leave.service';
import { LeaveRequest } from '../../types/leave';

export const LeaveApprovals: React.FC = () => {
  const [leaves, setLeaves] = useState<LeaveRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'ALL' | 'PENDING' | 'APPROVED' | 'REJECTED'>('PENDING');

  useEffect(() => {
    loadLeaves();
  }, []);

  const loadLeaves = async () => {
    try {
      const allLeaves = await leaveService.getAllLeaveRequests();
      setLeaves(allLeaves);
    } catch (err) {
      console.error('Failed to load leaves:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredLeaves = leaves.filter(leave => {
    if (filter === 'ALL') return true;
    return leave.status === filter;
  });

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
        <h1 className="text-3xl font-bold text-gray-800">Leave Approvals</h1>

        {/* Filter Buttons */}
        <div className="flex gap-2">
          {['ALL', 'PENDING', 'APPROVED', 'REJECTED'].map((status) => (
            <button
              key={status}
              onClick={() => setFilter(status as any)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === status
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        {/* Leave Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {filteredLeaves.length === 0 ? (
            <div className="col-span-2 bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
              No {filter.toLowerCase()} leave requests found
            </div>
          ) : (
            filteredLeaves.map((leave) => (
              <LeaveApprovalCard
                key={leave.id}
                leave={leave}
                onUpdate={loadLeaves}
              />
            ))
          )}
        </div>
      </div>
    </Layout>
  );
};
