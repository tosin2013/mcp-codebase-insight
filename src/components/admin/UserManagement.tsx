import React, { useState, useEffect } from 'react';
import { supabase } from '../../lib/supabase';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { SecuritySettingsModal } from './SecuritySettingsModal';
import { ProfileSettingsModal } from './ProfileSettingsModal';
import { ActivityLogModal } from './ActivityLogModal';
import { PasswordResetModal } from './PasswordResetModal';
import { 
  Users, Search, Filter, MapPin, Briefcase, 
  Calendar, MessageSquare, UserPlus, Star,
  Globe, Book, Award, Coffee, Shield, Lock,
  Activity, Settings, AlertTriangle
} from 'lucide-react';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'moderator' | 'admin';
  progress: {
    learningPaths: string[];
    contributions: number;
    badges: string[];
  };
}

export function UserManagement() {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showSecurityModal, setShowSecurityModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showActivityModal, setShowActivityModal] = useState(false);
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);

  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
    } else {
      navigate('/');
    }
  }, [isAdmin, navigate]);
  
  // Early return if not admin
  if (!isAdmin) {
    return null;
  }

  async function fetchUsers() {
    try {
      setLoading(true);
      setError(null);
      
      const { data, error: fetchError } = await supabase
        .rpc('get_users');

      if (fetchError) {
        if (fetchError.message.includes('Only administrators')) {
          navigate('/');
          return;
        } else {
          throw fetchError;
        }
      }

      const formattedUsers = (data || []).map(user => ({
        id: user.id,
        email: user.email || '',
        name: user.raw_user_meta_data?.name || '',
        role: user.raw_user_meta_data?.role || 'user',
        progress: user.raw_user_meta_data?.progress || {
          learningPaths: [],
          contributions: 0,
          badges: []
        }
      }));

      setUsers(formattedUsers);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to fetch users';
      console.error('Error fetching users:', errorMessage);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }

  async function updateUserRole(userId: string, newRole: 'user' | 'moderator' | 'admin') {
    try {
      setError(null);
      
      // Get current user data
      const currentUser = users.find(u => u.id === userId);
      if (!currentUser) throw new Error('User not found');

      const updatedMetadata = {
        ...currentUser,
        role: newRole
      };

      // Update user metadata through RPC function
      const { error: updateError } = await supabase
        .rpc('update_user_role', {
          user_id: userId,
          new_role: newRole,
          new_metadata: updatedMetadata
        });

      if (updateError) throw updateError;

      // Handle admin_users table through RPC
      const { error: manageError } = await supabase
        .rpc('manage_admin_user', {
          target_user_id: userId,
          is_admin: newRole === 'admin'
        });

      if (manageError) throw manageError;

      // Log the action
      await supabase.rpc('log_user_activity', {
        user_id: userId,
        action: `role_updated_to_${newRole}`,
        details: { previous_role: currentUser.role, new_role: newRole }
      });

      // Refresh user list
      await fetchUsers();
    } catch (err) {
      console.error('Error updating user role:', err);
      setError(err instanceof Error ? err.message : 'Failed to update user role');
    }
  }

  async function inviteUser(email: string, role: 'user' | 'moderator') {
    try {
      setError(null);

      // In a real app, this would send an invitation email
      // For now, we'll just create the user directly
      const { error: createError } = await supabase.rpc('create_user_if_not_exists', {
        user_email: email,
        user_password: 'temppass123', // In real app, this would be randomly generated
        user_metadata: {
          role,
          name: '',
          progress: {
            learningPaths: [],
            contributions: 0,
            badges: []
          }
        }
      });

      if (createError) throw createError;

      await fetchUsers();
      setShowInviteModal(false);
    } catch (err) {
      console.error('Error inviting user:', err);
      setError(err instanceof Error ? err.message : 'Failed to invite user');
    }
  }

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'all' || user.role === selectedRole;
    return matchesSearch && matchesRole;
  });

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="border-b border-gray-200 pb-5">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">User Management</h2>
              <p className="mt-2 text-sm text-gray-500">
                Manage user roles, permissions, and settings across the platform.
              </p>
            </div>
            <button
              onClick={() => setShowInviteModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <UserPlus className="h-4 w-4 mr-2" />
              Invite User
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-4 bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        <div className="mt-4 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search users..."
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              />
            </div>
          </div>
          <div>
            <select
              value={selectedRole}
              onChange={(e) => setSelectedRole(e.target.value as any)}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="all">All Roles</option>
              <option value="user">Users</option>
              <option value="moderator">Moderators</option>
              <option value="admin">Administrators</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="mt-6 flex justify-center">
            <div className="h-8 w-8 text-indigo-600 animate-spin" />
          </div>
        ) : (
          <div className="mt-6">
            <div className="flex flex-col">
              <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
                <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                  <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            User
                          </th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Role
                          </th>
                          <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Progress
                          </th>
                          <th scope="col" className="relative px-6 py-3">
                            <span className="sr-only">Actions</span>
                          </th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {filteredUsers.map((user) => (
                          <tr key={user.id}>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center">
                                <div>
                                  <div className="text-sm font-medium text-gray-900">
                                    {user.name || 'Unnamed User'}
                                  </div>
                                  <div className="text-sm text-gray-500">
                                    {user.email}
                                  </div>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full
                                ${user.role === 'admin' ? 'bg-red-100 text-red-800' : 
                                  user.role === 'moderator' ? 'bg-yellow-100 text-yellow-800' : 
                                  'bg-green-100 text-green-800'}`}>
                                {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                              </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              <div>Paths: {user.progress.learningPaths.length}</div>
                              <div>Contributions: {user.progress.contributions}</div>
                              <div>Badges: {user.progress.badges.length}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                              <div className="flex justify-end space-x-2">
                                <button
                                  onClick={() => {
                                    setSelectedUser(user);
                                    setShowProfileModal(true);
                                  }}
                                  className="text-gray-600 hover:text-gray-900"
                                >
                                  <Settings className="h-5 w-5" />
                                  <span className="sr-only">Profile Settings</span>
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedUser(user);
                                    setShowSecurityModal(true);
                                  }}
                                  className="text-gray-600 hover:text-gray-900"
                                >
                                  <Lock className="h-5 w-5" />
                                  <span className="sr-only">Security Settings</span>
                                </button>
                                <button
                                  onClick={() => {
                                    setSelectedUser(user);
                                    setShowActivityModal(true);
                                  }}
                                  className="text-gray-600 hover:text-gray-900"
                                >
                                  <Activity className="h-5 w-5" />
                                  <span className="sr-only">View Activity</span>
                                </button>
                                {user.role !== 'admin' && (
                                  <button
                                    onClick={() => updateUserRole(user.id, 'admin')}
                                   className="inline-flex items-center px-3 py-1.5 border border-indigo-300 rounded-md text-xs font-medium text-indigo-700 bg-indigo-50 hover:bg-indigo-100 tooltip"
                                    title="Make Admin"
                                  >
                                    <Shield className="h-5 w-5" />
                                   Make Admin
                                  </button>
                                )}
                                {user.role !== 'moderator' && (
                                  <button
                                    onClick={() => updateUserRole(user.id, 'moderator')}
                                   className="inline-flex items-center px-3 py-1.5 border border-yellow-300 rounded-md text-xs font-medium text-yellow-700 bg-yellow-50 hover:bg-yellow-100 tooltip"
                                    title="Make Moderator"
                                  >
                                    <Star className="h-5 w-5" />
                                   Make Moderator
                                  </button>
                                )}
                                {user.role !== 'user' && (
                                  <button
                                    onClick={() => updateUserRole(user.id, 'user')}
                                   className="inline-flex items-center px-3 py-1.5 border border-gray-300 rounded-md text-xs font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 tooltip"
                                    title="Remove Privileges"
                                  >
                                    <Users className="h-5 w-5" />
                                   Remove Privileges
                                  </button>
                                )}
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Profile Modal */}
      {showProfileModal && selectedUser && (
        <ProfileSettingsModal
          user={selectedUser}
          onClose={() => setShowProfileModal(false)}
          onUpdate={fetchUsers}
        />
      )}

      {/* Security Modal */}
      {showSecurityModal && selectedUser && (
        <SecuritySettingsModal
          user={selectedUser}
          onPasswordReset={() => setShowPasswordReset(true)}
          onClose={() => setShowSecurityModal(false)}
          onUpdate={fetchUsers}
        />
      )}

      {/* Activity Modal */}
      {showActivityModal && selectedUser && (
        <ActivityLogModal
          user={selectedUser}
          onClose={() => setShowActivityModal(false)}
        />
      )}

      {/* Password Reset Modal */}
      {showPasswordReset && selectedUser && (
        <PasswordResetModal
          user={selectedUser}
          onClose={() => setShowPasswordReset(false)}
          onUpdate={fetchUsers}
        />
      )}

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-lg w-full">
            <h3 className="text-lg font-medium text-gray-900">Invite New User</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target as HTMLFormElement);
              inviteUser(
                formData.get('email') as string,
                formData.get('role') as 'user' | 'moderator'
              );
            }}>
              <div className="mt-4">
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  id="email"
                  required
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                />
              </div>
              <div className="mt-4">
                <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                  Role
                </label>
                <select
                  name="role"
                  id="role"
                  required
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                >
                  <option value="user">User</option>
                  <option value="moderator">Moderator</option>
                </select>
              </div>
              <div className="mt-6 flex space-x-3">
                <button
                  type="submit"
                  className="flex-1 inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
                >
                  Send Invitation
                </button>
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="flex-1 inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}