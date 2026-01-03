/**
 * Salary Card Component
 * Displays salary breakdown
 */

import React from 'react';
import { SalaryInfo } from '../../types/payroll';
import { formatCurrency, formatDate } from '../../utils/helpers';

interface SalaryCardProps {
  salaryInfo: SalaryInfo;
}

export const SalaryCard: React.FC<SalaryCardProps> = ({ salaryInfo }) => {
  const { currentSalary } = salaryInfo;
  
  const grossSalary = 
    currentSalary.basicSalary +
    currentSalary.houseRent +
    currentSalary.transportAllowance +
    currentSalary.medicalAllowance +
    currentSalary.bonus;
  
  const netSalary = grossSalary - currentSalary.deductions;

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Salary Breakdown</h2>

      <div className="space-y-3 mb-6">
        <div className="flex justify-between py-2 border-b border-gray-200">
          <span className="text-gray-600">Basic Salary</span>
          <span className="font-medium text-gray-900">{formatCurrency(currentSalary.basicSalary)}</span>
        </div>
        <div className="flex justify-between py-2 border-b border-gray-200">
          <span className="text-gray-600">House Rent</span>
          <span className="font-medium text-gray-900">{formatCurrency(currentSalary.houseRent)}</span>
        </div>
        <div className="flex justify-between py-2 border-b border-gray-200">
          <span className="text-gray-600">Transport Allowance</span>
          <span className="font-medium text-gray-900">{formatCurrency(currentSalary.transportAllowance)}</span>
        </div>
        <div className="flex justify-between py-2 border-b border-gray-200">
          <span className="text-gray-600">Medical Allowance</span>
          <span className="font-medium text-gray-900">{formatCurrency(currentSalary.medicalAllowance)}</span>
        </div>
        <div className="flex justify-between py-2 border-b border-gray-200">
          <span className="text-gray-600">Bonus</span>
          <span className="font-medium text-gray-900">{formatCurrency(currentSalary.bonus)}</span>
        </div>
        <div className="flex justify-between py-2 border-b border-gray-200 bg-gray-50 px-2">
          <span className="font-semibold text-gray-700">Gross Salary</span>
          <span className="font-semibold text-gray-900">{formatCurrency(grossSalary)}</span>
        </div>
        <div className="flex justify-between py-2 border-b border-gray-200 text-red-600">
          <span className="text-gray-600">Deductions</span>
          <span className="font-medium">- {formatCurrency(currentSalary.deductions)}</span>
        </div>
      </div>

      <div className="bg-primary-50 p-4 rounded-lg">
        <div className="flex justify-between items-center">
          <span className="text-lg font-semibold text-gray-700">Net Salary</span>
          <span className="text-2xl font-bold text-primary-600">{formatCurrency(netSalary)}</span>
        </div>
      </div>

      <div className="mt-6 pt-6 border-t border-gray-200 grid grid-cols-2 gap-4">
        <div>
          <p className="text-sm text-gray-600">Last Increment</p>
          <p className="font-medium text-gray-900">{formatDate(salaryInfo.lastIncrement)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Next Review</p>
          <p className="font-medium text-gray-900">{formatDate(salaryInfo.nextReview)}</p>
        </div>
      </div>
    </div>
  );
};
