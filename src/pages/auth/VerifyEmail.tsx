/**
 * Verify Email Page
 * Placeholder for email verification
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { APP_NAME, ROUTES } from '../../utils/constants';
import { Button } from '../../components/common/Button';

export const VerifyEmail: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-md text-center">
        {/* Icon */}
        <div className="mb-6">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto">
            <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
        </div>

        {/* Content */}
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Verify Your Email</h1>
        <p className="text-gray-600 mb-6">
          We've sent a verification link to your email address. Please check your inbox and click the link to verify your account.
        </p>

        {/* Note */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 text-left">
          <p className="text-sm text-blue-800">
            <strong>Note:</strong> This is a demo app. Email verification is not implemented. You can proceed to login directly.
          </p>
        </div>

        {/* Action */}
        <Link to={ROUTES.LOGIN}>
          <Button fullWidth>Go to Login</Button>
        </Link>
      </div>
    </div>
  );
};
