/**
 * View Profile Page
 * Display user profile information with tabs
 */

import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/common/Button';
import { ROUTES } from '../../utils/constants';
import { formatDate, getInitials, formatCurrency } from '../../utils/helpers';
import * as authService from '../../services/auth.service';
import { User } from '../../types/user';

type ProfileTab = 'personal' | 'private' | 'salary' | 'security';

export const ViewProfile: React.FC = () => {
  const { user: currentUser } = useAuth();
  const { id } = useParams<{ id: string }>();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<ProfileTab>('personal');

  useEffect(() => {
    const loadUser = async () => {
      if (id) {
        try {
          const fetchedUser = await authService.getUserById(id);
          setUser(fetchedUser);
        } catch (error) {
          console.error('Failed to fetch user', error);
        }
      } else {
        setUser(currentUser);
      }
      setLoading(false);
    };
    loadUser();
  }, [id, currentUser]);

  if (loading) return <Layout><div>Loading...</div></Layout>;
  if (!user) return <Layout><div>User not found</div></Layout>;

  const isOwnProfile = currentUser?.id === user.id;
  const canEdit = isOwnProfile || currentUser?.role === 'ADMIN';

  const tabs: { id: ProfileTab; label: string; icon: string }[] = [
    { id: 'personal', label: 'Resume', icon: '📄' },
    { id: 'private', label: 'Private Info', icon: '🔒' },
    { id: 'salary', label: 'Salary Info', icon: '💰' },
    { id: 'security', label: 'Security', icon: '🛡️' },
  ];

  const renderPersonalTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">First Name</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.firstName}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Last Name</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.lastName}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Department</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.department}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Position</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.position}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Join Date</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {formatDate(user.joinDate)}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Role</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200">
            <span className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm font-medium">
              {user.role}
            </span>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPrivateTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.email}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.phone}
          </div>
        </div>
        <div className="col-span-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">Residential Address</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900 min-h-20">
            {user.address || 'Not provided'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Date of Birth</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.dob ? formatDate(user.dob) : 'Not provided'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Nationality</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.nationality || 'Not provided'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Personal Email</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.personalEmail || 'Not provided'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Gender</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.gender || 'Not provided'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Marital Status</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.maritalStatus || 'Not provided'}
          </div>
        </div>
      </div>
    </div>
  );

  const renderSalaryTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Annual Salary</label>
          <div className="px-4 py-3 bg-primary-50 rounded-lg border-2 border-primary-200 text-primary-900 font-semibold">
            {formatCurrency(840000)}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Monthly Salary</label>
          <div className="px-4 py-3 bg-primary-50 rounded-lg border-2 border-primary-200 text-primary-900 font-semibold">
            {formatCurrency(70000)}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Bank Name</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.bankName || 'Not provided'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Account Number</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.accountNumber || 'Not provided'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">IFSC Code</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.ifscCode || 'Not provided'}
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">PAN No.</label>
          <div className="px-4 py-3 bg-gray-50 rounded-lg border border-gray-200 text-gray-900">
            {user.panNo || 'Not provided'}
          </div>
        </div>
      </div>
    </div>
  );

  const renderSecurityTab = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-3">Security Settings</h3>
        <p className="text-sm text-blue-700 mb-4">Manage your account security and authentication methods.</p>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div>
            <h4 className="font-medium text-gray-900">Password</h4>
            <p className="text-sm text-gray-500">Last changed 3 months ago</p>
          </div>
          <Link to={ROUTES.PROFILE_EDIT}>
            <Button size="sm" variant="secondary">Change</Button>
          </Link>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div>
            <h4 className="font-medium text-gray-900">Two-Factor Authentication</h4>
            <p className="text-sm text-gray-500">Not enabled</p>
          </div>
          <div className="px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-medium">
            Disabled
          </div>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div>
            <h4 className="font-medium text-gray-900">Active Sessions</h4>
            <p className="text-sm text-gray-500">1 active session</p>
          </div>
          <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-medium">
            Active
          </span>
        </div>
      </div>
    </div>
  );

  return (
    <Layout>
      <div className="max-w-5xl mx-auto">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-8 text-white">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="w-28 h-28 rounded-full bg-white text-primary-600 flex items-center justify-center text-4xl font-bold shadow-lg">
                  {getInitials(user.firstName, user.lastName)}
                </div>
                <div>
                  <h1 className="text-3xl font-bold">{user.firstName} {user.lastName}</h1>
                  <p className="text-primary-100 mt-1 text-lg">{user.position}</p>
                  <p className="text-primary-200 text-sm mt-1">{user.department}</p>
                </div>
              </div>
              {canEdit && (
                <Link to={isOwnProfile ? ROUTES.PROFILE_EDIT : `/profile/edit/${user.id}`}>
                  <Button variant="secondary">Edit Profile</Button>
                </Link>
              )}
            </div>
          </div>

          {/* Tabs */}
          <div className="border-b border-gray-200 bg-gray-50 px-6">
            <div className="flex gap-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-4 font-medium text-sm transition-colors ${
                    activeTab === tab.id
                      ? 'text-primary-600 border-b-2 border-primary-600 bg-white'
                      : 'text-gray-600 hover:text-gray-800 border-b-2 border-transparent'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === 'personal' && renderPersonalTab()}
            {activeTab === 'private' && renderPrivateTab()}
            {activeTab === 'salary' && renderSalaryTab()}
            {activeTab === 'security' && renderSecurityTab()}
          </div>
        </div>
      </div>
    </Layout>
  );
};
