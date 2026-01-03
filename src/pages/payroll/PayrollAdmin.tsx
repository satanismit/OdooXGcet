/**
 * Payroll Admin Page
 * Admin page for managing employee payroll
 */

import React, { useEffect, useState } from 'react';
import { Layout } from '../../components/layout/Layout';
import { PayrollTable } from '../../components/payroll/PayrollTable';
import * as payrollService from '../../services/payroll.service';
import { PayrollRecord } from '../../types/payroll';

export const PayrollAdmin: React.FC = () => {
  const [payrollRecords, setPayrollRecords] = useState<PayrollRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPayrollData();
  }, []);

  const loadPayrollData = async () => {
    try {
      const records = await payrollService.getAllPayrollRecords();
      setPayrollRecords(records);
    } catch (err) {
      console.error('Failed to load payroll data:', err);
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
          <h1 className="text-3xl font-bold text-gray-800">Payroll Management</h1>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm text-gray-600">Total Employees</h3>
            <p className="text-2xl font-bold text-gray-800 mt-2">2</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm text-gray-600">Payroll Records</h3>
            <p className="text-2xl font-bold text-gray-800 mt-2">{payrollRecords.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-sm text-gray-600">Pending Payments</h3>
            <p className="text-2xl font-bold text-gray-800 mt-2">
              {payrollRecords.filter(r => r.status === 'PENDING').length}
            </p>
          </div>
        </div>

        {/* Payroll Table */}
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">All Payroll Records</h2>
          <PayrollTable records={payrollRecords} />
        </div>

        {/* Info Note */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <p className="text-sm text-blue-800">
            <strong>Note:</strong> This is a demo version. In production, you would have options to generate payroll, 
            update salaries, and process payments.
          </p>
        </div>
      </div>
    </Layout>
  );
};
