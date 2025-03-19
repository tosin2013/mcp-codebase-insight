import React from 'react';
import { 
  Users, 
  BookOpen, 
  Award, 
  Target, 
  Bell, 
  Shield, 
  Settings, 
  Link,
  Calendar,
  AlertTriangle,
  TrendingUp,
  Activity
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

// Dummy data for the activity chart
const activityData = [
  { time: '00:00', users: 120 },
  { time: '04:00', users: 80 },
  { time: '08:00', users: 250 },
  { time: '12:00', users: 480 },
  { time: '16:00', users: 380 },
  { time: '20:00', users: 220 },
  { time: '23:59', users: 150 },
];

// Recent system alerts
const alerts = [
  {
    id: 1,
    type: 'warning',
    message: 'High server load detected',
    time: '5 minutes ago'
  },
  {
    id: 2,
    type: 'info',
    message: 'New learning path published',
    time: '1 hour ago'
  },
  {
    id: 3,
    type: 'success',
    message: 'System backup completed',
    time: '3 hours ago'
  }
];

// Quick stats
const stats = [
  {
    name: 'Total Users',
    value: '915',
    change: '+12.5%',
    icon: Users,
    trend: 'up',
  },
  {
    name: 'Active Paths',
    value: '24',
    change: '+4.2%',
    icon: BookOpen,
    trend: 'up',
  },
  {
    name: 'Badges Awarded',
    value: '1,284',
    change: '+18.7%',
    icon: Award,
    trend: 'up',
  },
  {
    name: 'Completion Rate',
    value: '78%',
    change: '+5.4%',
    icon: Target,
    trend: 'up',
  },
];

// Quick actions
const quickActions = [
  {
    name: 'Manage Users',
    description: 'View and manage user accounts',
    icon: Users,
    href: '/admin/users',
    color: 'bg-blue-500'
  },
  {
    name: 'Learning Paths',
    description: 'Create and edit learning paths',
    icon: BookOpen,
    href: '/admin/paths',
    color: 'bg-green-500'
  },
  {
    name: 'External Links',
    description: 'Manage resource links',
    icon: Link,
    href: '/admin/links',
    color: 'bg-purple-500'
  },
  {
    name: 'Events',
    description: 'Manage tech events',
    icon: Calendar,
    href: '/admin/events',
    color: 'bg-yellow-500'
  },
  {
    name: 'Security',
    description: 'Review security settings',
    icon: Shield,
    href: '/admin/security',
    color: 'bg-red-500'
  },
  {
    name: 'Settings',
    description: 'Platform configuration',
    icon: Settings,
    href: '/admin/settings',
    color: 'bg-gray-500'
  }
];

export function Dashboard() {
  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        {/* Header */}
        <div className="border-b border-gray-200 pb-5">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Admin Dashboard</h2>
              <p className="mt-2 text-sm text-gray-500">
                Welcome back! Here's what's happening with your platform.
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button className="relative inline-flex items-center p-2 text-gray-400 hover:text-gray-500">
                <span className="sr-only">View notifications</span>
                <Bell className="h-6 w-6" />
                <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white" />
              </button>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
                <Activity className="h-4 w-4 mr-2" />
                View Analytics
              </button>
            </div>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
            <div
              key={stat.name}
              className="relative bg-white pt-5 px-4 pb-6 sm:pt-6 sm:px-6 shadow rounded-lg overflow-hidden"
            >
              <dt>
                <div className="absolute bg-indigo-500 rounded-md p-3">
                  <stat.icon className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                <p className="ml-16 text-sm font-medium text-gray-500 truncate">{stat.name}</p>
              </dt>
              <dd className="ml-16 flex items-baseline">
                <p className="text-2xl font-semibold text-gray-900">{stat.value}</p>
                <p
                  className={`ml-2 flex items-baseline text-sm font-semibold ${
                    stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {stat.change}
                  <TrendingUp
                    className={`self-center flex-shrink-0 h-4 w-4 ${
                      stat.trend === 'up' ? 'text-green-500' : 'text-red-500'
                    }`}
                    aria-hidden="true"
                  />
                </p>
              </dd>
            </div>
          ))}
        </div>

        <div className="mt-8 grid grid-cols-1 gap-8 lg:grid-cols-2">
          {/* Activity Chart */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Today's Activity</h3>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={activityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="users"
                    stroke="#4F46E5"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* System Alerts */}
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">System Alerts</h3>
            <div className="flow-root">
              <ul className="-mb-8">
                {alerts.map((alert, alertIdx) => (
                  <li key={alert.id}>
                    <div className="relative pb-8">
                      {alertIdx !== alerts.length - 1 ? (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      ) : null}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className={`
                            h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white
                            ${alert.type === 'warning' ? 'bg-yellow-500' :
                              alert.type === 'info' ? 'bg-blue-500' : 'bg-green-500'}
                          `}>
                            <AlertTriangle className="h-5 w-5 text-white" />
                          </span>
                        </div>
                        <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                          <div>
                            <p className="text-sm text-gray-500">{alert.message}</p>
                          </div>
                          <div className="text-right text-sm whitespace-nowrap text-gray-500">
                            <time dateTime={alert.time}>{alert.time}</time>
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {quickActions.map((action) => (
              <a
                key={action.name}
                href={action.href}
                className="relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400 focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-indigo-500"
              >
                <div className={`flex-shrink-0 h-10 w-10 rounded-md ${action.color} flex items-center justify-center`}>
                  <action.icon className="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="focus:outline-none">
                    <span className="absolute inset-0" aria-hidden="true" />
                    <p className="text-sm font-medium text-gray-900">{action.name}</p>
                    <p className="text-sm text-gray-500">{action.description}</p>
                  </div>
                </div>
              </a>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}