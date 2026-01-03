/**
 * Leave Approval Card Component
 * Card for approving/rejecting leave requests (Admin)
 */

import React, { useState } from 'react';
import { LeaveRequest } from '../../types/leave';
import { formatDate, getStatusColor } from '../../utils/helpers';
import { Button } from '../common/Button';
import * as leaveService from '../../services/leave.service';
import { useAuth } from '../../context/AuthContext';

interface LeaveApprovalCardProps {
  leave: LeaveRequest;
  onUpdate: () => void;
}

export const LeaveApprovalCard: React.FC<LeaveApprovalCardProps> = ({
  leave,
  onUpdate,
}) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [showRejectReason, setShowRejectReason] = useState(false);
  const [rejectReason, setRejectReason] = useState('');

  const handleApprove = async () => {
    if (!user) return;
    setLoading(true);
    try {
      await leaveService.updateLeaveStatus(
        leave.id,
        'APPROVED',
        `${user.firstName} ${user.lastName}`
      );
      onUpdate();
    } catch (err) {
      console.error('Failed to approve leave:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    if (!user || !rejectReason) return;
    setLoading(true);
    try {
      await leaveService.updateLeaveStatus(
        leave.id,
        'REJECTED',
        `${user.firstName} ${user.lastName}`,
        rejectReason
      );
      onUpdate();
    } catch (err) {
      console.error('Failed to reject leave:', err);
    } finally {
      setLoading(false);
      setShowRejectReason(false);
      setRejectReason('');
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border-l-4 border-yellow-400">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-800">{leave.userName}</h3>
          <p className="text-sm text-gray-500">Applied on {formatDate(leave.appliedOn)}</p>
        </div>
        <span className={`px-3 py-1 text-xs font-semibold rounded-full ${getStatusColor(leave.status)}`}>
          {leave.status}
        </span>
      </div>

      <div className="space-y-2 mb-4">
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Leave Type:</span>
          <span className="text-sm font-medium text-gray-900">{leave.leaveType}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-sm text-gray-600">Duration:</span>
          <span className="text-sm font-medium text-gray-900">
            {formatDate(leave.startDate)} - {formatDate(leave.endDate)} ({leave.totalDays} days)
          </span>
        </div>
        <div>
          <span className="text-sm text-gray-600">Reason:</span>
          <p className="text-sm text-gray-900 mt-1">{leave.reason}</p>
        </div>
      </div>

      {leave.status === 'PENDING' && (
        <div className="space-y-2">
          {showRejectReason ? (
            <div className="space-y-2">
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                placeholder="Reason for rejection"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500"
                rows={3}
              />
              <div className="flex gap-2">
                <Button
                  onClick={handleReject}
                  variant="danger"
                  size="sm"
                  isLoading={loading}
                  fullWidth
                >
                  Confirm Reject
                </Button>
                <Button
                  onClick={() => setShowRejectReason(false)}
                  variant="secondary"
                  size="sm"
                  fullWidth
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex gap-2">
              <Button
                onClick={handleApprove}
                variant="success"
                size="sm"
                isLoading={loading}
                fullWidth
              >
                Approve
              </Button>
              <Button
                onClick={() => setShowRejectReason(true)}
                variant="danger"
                size="sm"
                fullWidth
              >
                Reject
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
