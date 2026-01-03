/**
 * Not Found Page
 * 404 error page
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/common/Button';
import { ROUTES } from '../utils/constants';

export const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-9xl font-bold text-primary-600">404</h1>
        <p className="text-2xl font-semibold text-gray-800 mt-4">Page Not Found</p>
        <p className="text-gray-600 mt-2 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link to={ROUTES.EMPLOYEE_DASHBOARD}>
          <Button>Go to Dashboard</Button>
        </Link>
      </div>
    </div>
  );
};
