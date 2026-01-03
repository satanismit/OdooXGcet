/**
 * My Salary Page
 * Employee salary view page
 */

import React, { useEffect, useState } from 'react';
import { Layout } from '../../components/layout/Layout';
import { SalaryCard } from '../../components/payroll/SalaryCard';
import { PayrollTable } from '../../components/payroll/PayrollTable';
import { useAuth } from '../../context/AuthContext';
import * as payrollService from '../../services/payroll.service';
import { SalaryInfo, PayrollRecord } from '../../types/payroll';
import { formatCurrency } from '../../utils/helpers';

export const MySalary: React.FC = () => {
  const { user } = useAuth();
  const [salaryInfo, setSalaryInfo] = useState<SalaryInfo | null>(null);
  const [payrollRecords, setPayrollRecords] = useState<PayrollRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSalaryData();
  }, []);

  const loadSalaryData = async () => {
    if (!user) return;
    try {
      const [salary, records] = await Promise.all([
        payrollService.getSalaryInfo(user.id),
        payrollService.getPayrollRecords(user.id),
      ]);
      setSalaryInfo(salary);
      setPayrollRecords(records);
    } catch (err) {
      console.error('Failed to load salary data:', err);
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
        <h1 className="text-3xl font-bold text-gray-800">My Salary</h1>

        {/* Annual Salary Card */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg shadow-md p-6 text-white">
          <h2 className="text-lg font-medium opacity-90">Annual Salary (CTC)</h2>
          <p className="text-4xl font-bold mt-2">
            {salaryInfo ? formatCurrency(salaryInfo.annualSalary) : '—'}
          </p>
          <p className="text-sm opacity-75 mt-1">Per year</p>
        </div>

        {/* Salary Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {salaryInfo && <SalaryCard salaryInfo={salaryInfo} />}
          
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Quick Stats</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                <span className="text-gray-600">Monthly Salary</span>
                <span className="font-semibold text-blue-600">
                  {salaryInfo ? formatCurrency(salaryInfo.annualSalary / 12) : '—'}
                </span>
              </div>
              <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                <span className="text-gray-600">Total Payments</span>
                <span className="font-semibold text-green-600">{payrollRecords.length}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Payroll History */}
        <div>
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Payroll History</h2>
          <PayrollTable records={payrollRecords} />
        </div>
      </div>
    </Layout>
  );
};
