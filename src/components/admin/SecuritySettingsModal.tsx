import React, { useState } from 'react';
import { supabase } from '../../lib/supabase';
import { Lock, Shield, Bell, Globe, Key } from 'lucide-react';
import type { User } from '../../types';

interface SecuritySettingsModalProps {
  user: User;
  onClose: () => void;
  onPasswordReset: () => void;
  onUpdate: () => void;
}

export function SecuritySettingsModal({ user, onClose, onPasswordReset, onUpdate }: SecuritySettingsModalProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    twoFactorEnabled: false,
    loginNotifications: true,
    allowedIps: [] as string[],
    securityQuestions: {} as Record<string, string>
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { error: updateError } = await supabase.rpc('update_security_settings', {
        target_user_id: user.id,
        two_factor_enabled: formData.twoFactorEnabled,
        login_notifications: formData.loginNotifications,
        allowed_ips: JSON.stringify(formData.allowedIps)
      });

      if (updateError) throw updateError;

      // Log the security update
      await supabase.rpc('log_user_activity', {
        user_id: user.id,
        action: 'security_settings_updated',
        details: {
          two_factor_enabled: formData.twoFactorEnabled,
          login_notifications: formData.loginNotifications
        }
      });

      onUpdate();
      onClose();
    } catch (err) {
      console.error('Error updating security settings:', err);
      setError(err instanceof Error ? err.message : 'Failed to update security settings');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4">
        <div className="px-6 py-4 bg-indigo-600 text-white flex justify-between items-center">
          <h3 className="text-lg font-medium flex items-center">
            <Shield className="h-5 w-5 mr-2" />
            Security Settings for {user.name || user.email}
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
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Lock className="h-5 w-5 text-gray-400 mr-2" />
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Two-Factor Authentication
                  </label>
                  <p className="text-sm text-gray-500">
                    Add an extra layer of security to your account
                  </p>
                </div>
              </div>
              <div className="ml-4">
                <input
                  type="checkbox"
                  checked={formData.twoFactorEnabled}
                  onChange={(e) => setFormData({ ...formData, twoFactorEnabled: e.target.checked })}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <Bell className="h-5 w-5 text-gray-400 mr-2" />
                <div>
                  <label className="block text-sm font-medium text-gray-700">
                    Login Notifications
                  </label>
                  <p className="text-sm text-gray-500">
                    Receive notifications for new login attempts
                  </p>
                </div>
              </div>
              <div className="ml-4">
                <input
                  type="checkbox"
                  checked={formData.loginNotifications}
                  onChange={(e) => setFormData({ ...formData, loginNotifications: e.target.checked })}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
              </div>
            </div>

            <div>
              <div className="flex items-center">
                <Globe className="h-5 w-5 text-gray-400 mr-2" />
                <label className="block text-sm font-medium text-gray-700">
                  IP Address Restrictions
                </label>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                Restrict login access to specific IP addresses (optional)
              </p>
              <div className="mt-2">
                <input
                  type="text"
                  placeholder="Enter IP addresses (comma-separated)"
                  value={formData.allowedIps.join(', ')}
                  onChange={(e) => setFormData({
                    ...formData,
                    allowedIps: e.target.value.split(',').map(ip => ip.trim()).filter(Boolean)
                  })}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>
          </div>

          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => {
                onClose();
                // Show password reset modal
                onPasswordReset();
              }}
              className="inline-flex items-center px-4 py-2 border border-yellow-300 rounded-md shadow-sm text-sm font-medium text-yellow-700 bg-yellow-50 hover:bg-yellow-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-yellow-500"
            >
              <Key className="h-4 w-4 mr-2" />
              Reset Password
            </button>
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