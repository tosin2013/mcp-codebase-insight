import React, { useState } from 'react';
import { ChevronDown, Settings, Link, Users, BarChart } from 'lucide-react';

export function AdminMenu() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1 px-3 py-1.5 text-sm font-medium text-indigo-600 bg-indigo-50 rounded-md hover:bg-indigo-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        <Settings className="h-4 w-4" />
        <span>Admin</span>
        <ChevronDown className={`h-4 w-4 transform transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-50">
          <div className="py-1" role="menu" aria-orientation="vertical">
            <a
              href="/admin/links"
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              role="menuitem"
            >
              <Link className="h-4 w-4 mr-2" />
              Manage Links
            </a>
            <a
              href="/admin/users"
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              role="menuitem"
            >
              <Users className="h-4 w-4 mr-2" />
              User Management
            </a>
            <a
              href="/admin/analytics"
              className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              role="menuitem"
            >
              <BarChart className="h-4 w-4 mr-2" />
              Analytics
            </a>
          </div>
        </div>
      )}
    </div>
  );
}