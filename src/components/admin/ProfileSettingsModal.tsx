import React, { useState } from 'react';
import { supabase } from '../../lib/supabase';
import { User, Settings, Mail, User as UserIcon } from 'lucide-react';
import type { User as UserType } from '../../types';

interface ProfileSettingsModalProps {
  user: UserType;
  onClose: () => void;
  onUpdate: () => void;
}

export function ProfileSettingsModal({ user, onClose, onUpdate }: ProfileSettingsModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    name: user.name || '',
    email: user.email,
    role: user.role,
    preferences: {
      emailNotifications: true,
      ...user.preferences
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Update user profile through RPC function
      const { error: updateError } = await supabase.rpc('upsert_user_profile', {
        user_id: user.id,
        display_name: formData.name,
        preferences: JSON.stringify(formData.preferences)
      });

      if (updateError) throw updateError;

      // Log the profile update
      await supabase.rpc('log_user_activity', {
        user_id: user.id,
        action: 'profile_updated',
        details: { updated_fields: ['name', 'preferences'] }
      });

      onUpdate();
      onClose();
    } catch (err) {
      console.error('Error updating profile:', err);
      setError(err instanceof Error ? err.message : 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4">
        <div className="px-6 py-4 bg-indigo-600 text-white flex justify-between items-center">
          <h3 className="text-lg font-medium flex items-center">
            <Settings className="h-5 w-5 mr-2" />
            Profile Settings for {user.name || user.email}
          </h3>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-4 bg-red-50 border-l-4 border-red-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">⚠</div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-6">
            <div>
              <label htmlFor="name" className="flex items-center text-sm font-medium text-gray-700">
                <UserIcon className="h-5 w-5 text-gray-400 mr-2" />
                Display Name
              </label>
              <input
                type="text"
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="mt-1 block w-full shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm border-gray-300 rounded-md"
              />
            </div>

            <div>
              <label htmlFor="email" className="flex items-center text-sm font-medium text-gray-700">
                <Mail className="h-5 w-5 text-gray-400 mr-2" />
                Email Address
              </label>
              <input
                type="email"
                id="email"
                value={formData.email}
                disabled
                className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md bg-gray-50"
              />
              <p className="mt-1 text-sm text-gray-500">Email address cannot be changed</p>
            </div>

            <div>
              <label className="flex items-center text-sm font-medium text-gray-700">
                <User className="h-5 w-5 text-gray-400 mr-2" />
                Role
                <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Current Role
                </span>
              </label>
              <input
                type="text"
                value={formData.role.charAt(0).toUpperCase() + formData.role.slice(1)}
                disabled
                className="mt-1 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md bg-gray-50"
              />
              <p className="mt-1 text-sm text-gray-500">
                Role can be changed using the role management buttons in the user list
              </p>
            </div>

            <div className="pt-4">
              <h4 className="text-sm font-medium text-gray-900 mb-4">Preferences</h4>
              <div className="space-y-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="emailNotifications"
                    checked={formData.preferences.emailNotifications}
                    onChange={(e) => setFormData({
                      ...formData,
                      preferences: {
                        ...formData.preferences,
                        emailNotifications: e.target.checked
                      }
                    })}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="emailNotifications" className="ml-2 block text-sm text-gray-700">
                    Receive email notifications
                  </label>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="inline-flex justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}