/**
 * Apply Leave Form Component
 * Form for applying new leave requests
 */

import React, { useState } from 'react';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { Modal } from '../common/Modal';
import { LeaveType } from '../../types/leave';
import { useAuth } from '../../context/AuthContext';
import * as leaveService from '../../services/leave.service';

interface ApplyLeaveFormProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ApplyLeaveForm: React.FC<ApplyLeaveFormProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const { user } = useAuth();
  const [formData, setFormData] = useState({
    leaveType: 'PAID' as LeaveType,
    startDate: '',
    endDate: '',
    reason: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;

    setLoading(true);
    setError('');

    try {
      await leaveService.applyLeave(
        user.id,
        `${user.firstName} ${user.lastName}`,
        formData.leaveType,
        formData.startDate,
        formData.endDate,
        formData.reason
      );
      onSuccess();
      onClose();
      setFormData({ leaveType: 'PAID', startDate: '', endDate: '', reason: '' });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Apply for Leave">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="p-3 bg-red-100 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Leave Type <span className="text-red-500">*</span>
          </label>
          <select
            value={formData.leaveType}
            onChange={(e) => setFormData({ ...formData, leaveType: e.target.value as LeaveType })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            required
          >
            <option value="PAID">Paid Leave</option>
            <option value="SICK">Sick Leave</option>
            <option value="CASUAL">Casual Leave</option>
            <option value="UNPAID">Unpaid Leave</option>
          </select>
        </div>

        <Input
          type="date"
          label="Start Date"
          value={formData.startDate}
          onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
          required
        />

        <Input
          type="date"
          label="End Date"
          value={formData.endDate}
          onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
          required
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Reason <span className="text-red-500">*</span>
          </label>
          <textarea
            value={formData.reason}
            onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            rows={4}
            required
          />
        </div>

        <div className="flex gap-3 pt-4">
          <Button type="button" variant="secondary" onClick={onClose} fullWidth>
            Cancel
          </Button>
          <Button type="submit" isLoading={loading} fullWidth>
            Submit
          </Button>
        </div>
      </form>
    </Modal>
  );
};
