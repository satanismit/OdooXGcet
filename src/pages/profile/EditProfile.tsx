/**
 * Edit Profile Page
 * Edit user profile information
 */

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Layout } from '../../components/layout/Layout';
import { useAuth } from '../../context/AuthContext';
import { Input } from '../../components/common/Input';
import { Button } from '../../components/common/Button';
import { ROUTES } from '../../utils/constants';
import * as authService from '../../services/auth.service';
import { User } from '../../types/user';

export const EditProfile: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const { user: currentUser, updateUser } = useAuth();
  const [formData, setFormData] = useState<Partial<User>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadUser = async () => {
      if (id) {
        try {
          const fetchedUser = await authService.getUserById(id);
          if (fetchedUser) {
            setFormData(fetchedUser);
          } else {
            setError('User not found');
          }
        } catch (err) {
          setError('Failed to fetch user');
        }
      } else if (currentUser) {
        setFormData(currentUser);
      }
      setLoading(false);
    };
    loadUser();
  }, [id, currentUser]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      if (id) {
        await authService.updateUserById(id, formData);
        navigate(`/profile/${id}`);
      } else {
        await updateUser(formData);
        navigate(ROUTES.PROFILE_VIEW);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  if (loading) return <Layout><div>Loading...</div></Layout>;

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-6">
            {id ? 'Edit Employee Profile' : 'Edit My Profile'}
          </h1>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="First Name"
                name="firstName"
                value={formData.firstName || ''}
                onChange={handleChange}
                required
              />
              <Input
                label="Last Name"
                name="lastName"
                value={formData.lastName || ''}
                onChange={handleChange}
                required
              />
            </div>
            
            <Input
              label="Phone Number"
              name="phone"
              value={formData.phone || ''}
              onChange={handleChange}
            />
            
            <Input
              label="Address"
              name="address"
              value={formData.address || ''}
              onChange={handleChange}
            />

            {/* Admin Only Fields */}
            {(currentUser?.role === 'ADMIN') && (
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200 space-y-4">
                <h3 className="font-medium text-gray-900">Admin Settings</h3>
                <div className="grid grid-cols-2 gap-4">
                  <Input
                    label="Department"
                    name="department"
                    value={formData.department || ''}
                    onChange={handleChange}
                  />
                  <Input
                    label="Position"
                    name="position"
                    value={formData.position || ''}
                    onChange={handleChange}
                  />
                </div>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-100 text-red-700 rounded-md text-sm">
                {error}
              </div>
            )}

            <div className="flex justify-end gap-3 pt-4">
              <Button 
                type="button" 
                variant="secondary" 
                onClick={() => navigate(-1)}
              >
                Cancel
              </Button>
              <Button type="submit" isLoading={saving}>
                Save Changes
              </Button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
};
