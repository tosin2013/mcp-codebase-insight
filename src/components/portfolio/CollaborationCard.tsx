import React from 'react';
import { Calendar, Users, CheckCircle, Clock } from 'lucide-react';
import type { Collaboration } from '../../types';

interface CollaborationCardProps {
  collaboration: Collaboration;
}

export function CollaborationCard({ collaboration }: CollaborationCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'completed':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-start">
        <h3 className="text-lg font-medium text-gray-900">{collaboration.role}</h3>
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(collaboration.status)}`}>
          {collaboration.status.charAt(0).toUpperCase() + collaboration.status.slice(1)}
        </span>
      </div>

      <div className="mt-4 space-y-2">
        <div className="flex items-center text-sm text-gray-500">
          <Calendar className="h-4 w-4 mr-2" />
          <span>
            {new Date(collaboration.startDate).toLocaleDateString()} - 
            {collaboration.endDate ? new Date(collaboration.endDate).toLocaleDateString() : 'Present'}
          </span>
        </div>

        <div className="flex items-center text-sm text-gray-500">
          <Users className="h-4 w-4 mr-2" />
          <span>Project ID: {collaboration.projectId}</span>
        </div>
      </div>

      <div className="mt-6 flex justify-between items-center">
        <button className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200">
          <CheckCircle className="h-4 w-4 mr-1" />
          Update Status
        </button>
        <button className="inline-flex items-center text-sm text-gray-500 hover:text-indigo-600">
          <Clock className="h-4 w-4 mr-1" />
          View Timeline
        </button>
      </div>
    </div>
  );
}