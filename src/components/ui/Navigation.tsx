import React from 'react';
import { Menu, X, BookOpen, Code, Users, Layout, MessageSquare, HelpCircle, Mail } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { AdminMenu } from '../admin/AdminMenu';
import type { NavigationItem } from '../../types';

const navigationItems: NavigationItem[] = [
  { 
    title: 'Learn', 
    href: '/learn', 
    description: 'Access curated learning paths and resources',
    icon: BookOpen 
  },
  { 
    title: 'Contribute', 
    href: '/contribute', 
    description: 'Join open-source projects and challenges',
    icon: Code 
  },
  { 
    title: 'Network', 
    href: '/network', 
    description: 'Connect with peers and mentors',
    icon: Users 
  },
  { 
    title: 'Portfolio', 
    href: '/portfolio', 
    description: 'Build and showcase your work',
    icon: Layout 
  },
  { 
    title: 'Community', 
    href: '/community', 
    description: 'Join discussions and get feedback',
    icon: MessageSquare 
  },
  { 
    title: 'About', 
    href: '/about', 
    description: 'Learn about our mission',
    icon: HelpCircle 
  },
  { 
    title: 'Contact', 
    href: '/contact', 
    description: 'Get support and help',
    icon: Mail 
  }
];

export function Navigation() {
  const [isOpen, setIsOpen] = React.useState(false);
  const { user, isAdmin, signOut } = useAuth();

  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <a href="/" className="text-2xl font-bold text-indigo-600">TechPath</a>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navigationItems.map((item) => {
                const Icon = item.icon;
                return (
                  <a
                    key={item.href}
                    href={item.href}
                    className="inline-flex items-center px-1 pt-1 text-sm font-medium text-gray-900 hover:text-indigo-600"
                  >
                    {Icon && <Icon className="h-4 w-4 mr-1" />}
                    {item.title}
                  </a>
                );
              })}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            {user ? (
              <div className="flex items-center space-x-4">
                {isAdmin && <AdminMenu />}
                <div className="hidden md:flex flex-col items-end">
                  <span className="text-sm font-medium text-gray-900">
                    {user.email}
                  </span>
                  <span className="text-xs text-gray-500">
                    {isAdmin ? 'Administrator' : 'Member'}
                  </span>
                </div>
                <div className="flex space-x-2">
                  <a
                    href="/dashboard"
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-indigo-600 hover:bg-indigo-700"
                  >
                    Dashboard
                  </a>
                  <button
                    onClick={() => signOut()}
                    className="inline-flex items-center px-3 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <a
                  href="/sign-in"
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-indigo-600 bg-indigo-50 hover:bg-indigo-100"
                >
                  Sign In
                </a>
                <a
                  href="/sign-up"
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Sign Up
                </a>
              </div>
            )}
            <div className="flex items-center sm:hidden">
              <button
                onClick={() => setIsOpen(!isOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isOpen && (
        <div className="sm:hidden">
          <div className="pt-2 pb-3 space-y-1">
            {navigationItems.map((item) => {
              const Icon = item.icon;
              return (
                <a
                  key={item.href}
                  href={item.href}
                  className="flex items-center px-3 py-2 text-base font-medium text-gray-700 hover:text-indigo-600 hover:bg-gray-50"
                >
                  {Icon && <Icon className="h-4 w-4 mr-2" />}
                  {item.title}
                  {item.description && (
                    <span className="ml-2 text-sm text-gray-500">{item.description}</span>
                  )}
                </a>
              );
            })}
            {user && isAdmin && (
              <>
                <div className="border-t border-gray-200 my-2"></div>
                <a
                  href="/admin/links"
                  className="flex items-center px-3 py-2 text-base font-medium text-indigo-600 hover:bg-gray-50"
                >
                  Manage Links
                </a>
                <a
                  href="/admin/users"
                  className="flex items-center px-3 py-2 text-base font-medium text-indigo-600 hover:bg-gray-50"
                >
                  User Management
                </a>
                <a
                  href="/admin/analytics"
                  className="flex items-center px-3 py-2 text-base font-medium text-indigo-600 hover:bg-gray-50"
                >
                  Analytics
                </a>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
}