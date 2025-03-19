import React from 'react';
import { MessageSquare, Users, Code, Calendar } from 'lucide-react';

interface CollaborationRequest {
  id: string;
  title: string;
  author: {
    name: string;
    avatar: string;
  };
  type: 'project' | 'mentorship' | 'pair-programming';
  description: string;
  skills: string[];
  timeframe: string;
  responses: number;
  status: 'open' | 'in-progress' | 'closed';
}

const collaborationRequests: CollaborationRequest[] = [
  {
    id: '1',
    title: 'Looking for React mentor',
    author: {
      name: 'Emily Johnson',
      avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    type: 'mentorship',
    description: 'Seeking an experienced React developer to mentor me through building a complex application with Redux and TypeScript.',
    skills: ['React', 'Redux', 'TypeScript'],
    timeframe: '3 months',
    responses: 4,
    status: 'open'
  },
  {
    id: '2',
    title: 'Backend developer needed for open-source project',
    author: {
      name: 'Michael Torres',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80'
    },
    type: 'project',
    description: 'Looking for a Node.js developer to help build the backend for an open-source project management tool.',
    skills: ['Node.js', 'Express', 'PostgreSQL'],
    timeframe: '6 months',
    responses: 7,
    status: 'open'
  }
];

export function CollaborationBoard() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Collaboration Board</h2>
        <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
          <MessageSquare className="h-4 w-4 mr-2" />
          Post Request
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {collaborationRequests.map((request) => (
          <div key={request.id} className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex justify-between items-start">
              <div className="flex items-center space-x-3">
                <img
                  src={request.author.avatar}
                  alt={request.author.name}
                  className="h-10 w-10 rounded-full"
                />
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{request.title}</h3>
                  <p className="text-sm text-gray-500">Posted by {request.author.name}</p>
                </div>
              </div>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                request.status === 'open'
                  ? 'bg-green-100 text-green-800'
                  : request.status === 'in-progress'
                  ? 'bg-yellow-100 text-yellow-800'
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
              </span>
            </div>

            <div className="mt-4">
              <p className="text-sm text-gray-600">{request.description}</p>
            </div>

            <div className="mt-4 flex flex-wrap gap-2">
              {request.skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                >
                  <Code className="h-3 w-3 mr-1" />
                  {skill}
                </span>
              ))}
            </div>

            <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
              <div className="flex space-x-4">
                <span className="flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  {request.timeframe}
                </span>
                <span className="flex items-center">
                  <MessageSquare className="h-4 w-4 mr-1" />
                  {request.responses} responses
                </span>
              </div>
              <button className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                <Users className="h-4 w-4 mr-1" />
                Respond
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}