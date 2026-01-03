/**
 * Sidebar Component
 * Navigation sidebar with role-based menu items
 */

import React from 'react';
import { NavLink } from 'react-router-dom';
import { useUser } from '../../context/UserContext';
import { ROUTES } from '../../utils/constants';

interface MenuItem {
  name: string;
  path: string;
  icon: string;
  adminOnly?: boolean;
}

const menuItems: MenuItem[] = [
  {
    name: 'Dashboard',
    path: ROUTES.EMPLOYEE_DASHBOARD,
    icon: '📊',
  },
  {
    name: 'Profile',
    path: ROUTES.PROFILE_VIEW,
    icon: '👤',
  },
  {
    name: 'Attendance',
    path: ROUTES.ATTENDANCE,
    icon: '📅',
  },
  {
    name: 'My Leaves',
    path: ROUTES.MY_LEAVES,
    icon: '🏖️',
  },
  {
    name: 'My Salary',
    path: ROUTES.MY_SALARY,
    icon: '💰',
  },
  {
    name: 'Admin Dashboard',
    path: ROUTES.ADMIN_DASHBOARD,
    icon: '⚙️',
    adminOnly: true,
  },
  {
    name: 'Leave Approvals',
    path: ROUTES.LEAVE_APPROVALS,
    icon: '✅',
    adminOnly: true,
  },
  {
    name: 'Payroll Admin',
    path: ROUTES.PAYROLL_ADMIN,
    icon: '💵',
    adminOnly: true,
  },
];

export const Sidebar: React.FC = () => {
  const { isAdmin } = useUser();

  const filteredItems = menuItems.filter(item => {
    if (item.adminOnly && !isAdmin) return false;
    if (!item.adminOnly && isAdmin && item.path === ROUTES.EMPLOYEE_DASHBOARD) return false;
    return true;
  });

  return (
    <aside className="w-64 bg-gray-50 border-r border-gray-200 min-h-screen">
      <nav className="p-4 space-y-2">
        {filteredItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                isActive
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-700 hover:bg-gray-200'
              }`
            }
          >
            <span className="text-xl">{item.icon}</span>
            <span className="font-medium">{item.name}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
