import React, { useState } from 'react';
import { 
  Users, Search, Filter, MapPin, Briefcase, 
  Calendar, MessageSquare, UserPlus, Star,
  Globe, Book, Award, Coffee
} from 'lucide-react';

interface NetworkMember {
  id: string;
  name: string;
  role: string;
  company: string;
  location: string;
  avatar: string;
  skills: string[];
  interests: string[];
  availability: 'open' | 'limited' | 'busy';
  mentoring: boolean;
  lastActive: string;
}

interface MeetupEvent {
  id: string;
  title: string;
  date: string;
  location: string;
  attendees: number;
  type: 'virtual' | 'in-person';
  tags: string[];
}

const networkMembers: NetworkMember[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    role: 'Senior Frontend Developer',
    company: 'TechCorp',
    location: 'San Francisco, CA',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    skills: ['React', 'TypeScript', 'GraphQL'],
    interests: ['Mentoring', 'Open Source', 'UI/UX'],
    availability: 'open',
    mentoring: true,
    lastActive: '2 hours ago'
  },
  {
    id: '2',
    name: 'Michael Torres',
    role: 'Cloud Architect',
    company: 'CloudScale',
    location: 'Seattle, WA',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    skills: ['AWS', 'Kubernetes', 'Terraform'],
    interests: ['Cloud Architecture', 'DevOps', 'Scalability'],
    availability: 'limited',
    mentoring: true,
    lastActive: '1 day ago'
  }
];

const meetupEvents: MeetupEvent[] = [
  {
    id: '1',
    title: 'Frontend Developer Meetup',
    date: '2024-03-15T18:00:00Z',
    location: 'San Francisco, CA',
    attendees: 45,
    type: 'in-person',
    tags: ['React', 'JavaScript', 'Web Development']
  },
  {
    id: '2',
    title: 'Cloud Computing Workshop',
    date: '2024-03-20T15:00:00Z',
    location: 'Online',
    attendees: 120,
    type: 'virtual',
    tags: ['AWS', 'Cloud', 'DevOps']
  }
];

export function NetworkPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [selectedAvailability, setSelectedAvailability] = useState<string>('all');
  const [activeTab, setActiveTab] = useState<'professionals' | 'events'>('professionals');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-indigo-700 text-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-3xl font-extrabold sm:text-4xl">
              Connect with Tech Professionals
            </h1>
            <p className="mt-3 text-xl text-indigo-200">
              Build meaningful connections, find mentors, and grow together
            </p>
          </div>

          {/* Quick Stats */}
          <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Users className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">5,000+</div>
                  <div className="text-indigo-200">Active Members</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Book className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">200+</div>
                  <div className="text-indigo-200">Mentors</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Calendar className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">50+</div>
                  <div className="text-indigo-200">Monthly Events</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, role, or skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => setActiveTab('professionals')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'professionals'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Users className="h-5 w-5 inline-block mr-2" />
                Professionals
              </button>
              <button
                onClick={() => setActiveTab('events')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'events'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Calendar className="h-5 w-5 inline-block mr-2" />
                Events
              </button>
            </div>
          </div>
        </div>

        {activeTab === 'professionals' && (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {networkMembers.map((member) => (
              <div key={member.id} className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex items-start space-x-4">
                  <img
                    src={member.avatar}
                    alt={member.name}
                    className="h-12 w-12 rounded-full"
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-medium text-gray-900">{member.name}</h3>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        member.availability === 'open' 
                          ? 'bg-green-100 text-green-800'
                          : member.availability === 'limited'
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {member.availability.charAt(0).toUpperCase() + member.availability.slice(1)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500">{member.role}</p>
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <Briefcase className="h-4 w-4 mr-1" />
                      {member.company}
                    </div>
                    <div className="mt-1 flex items-center text-sm text-gray-500">
                      <MapPin className="h-4 w-4 mr-1" />
                      {member.location}
                    </div>
                  </div>
                </div>

                <div className="mt-4">
                  <div className="flex flex-wrap gap-2">
                    {member.skills.map((skill) => (
                      <span
                        key={skill}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 flex justify-between items-center">
                  <div className="flex space-x-2">
                    <button className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                      <UserPlus className="h-4 w-4 mr-1" />
                      Connect
                    </button>
                    <button className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200">
                      <MessageSquare className="h-4 w-4 mr-1" />
                      Message
                    </button>
                  </div>
                  {member.mentoring && (
                    <span className="inline-flex items-center text-sm text-indigo-600">
                      <Award className="h-4 w-4 mr-1" />
                      Available for Mentoring
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'events' && (
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
            {meetupEvents.map((event) => (
              <div key={event.id} className="bg-white rounded-lg shadow-sm p-6">
                <div className="flex justify-between items-start">
                  <h3 className="text-lg font-medium text-gray-900">{event.title}</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    event.type === 'virtual'
                      ? 'bg-blue-100 text-blue-800'
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {event.type === 'virtual' ? (
                      <Globe className="h-4 w-4 mr-1" />
                    ) : (
                      <MapPin className="h-4 w-4 mr-1" />
                    )}
                    {event.type.charAt(0).toUpperCase() + event.type.slice(1)}
                  </span>
                </div>

                <div className="mt-2 space-y-2">
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="h-4 w-4 mr-1" />
                    {new Date(event.date).toLocaleDateString(undefined, {
                      weekday: 'long',
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric',
                      hour: 'numeric',
                      minute: 'numeric'
                    })}
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <MapPin className="h-4 w-4 mr-1" />
                    {event.location}
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <Users className="h-4 w-4 mr-1" />
                    {event.attendees} attendees
                  </div>
                </div>

                <div className="mt-4">
                  <div className="flex flex-wrap gap-2">
                    {event.tags.map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 flex justify-between items-center">
                  <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                    <Calendar className="h-4 w-4 mr-2" />
                    RSVP
                  </button>
                  <button className="inline-flex items-center text-sm text-indigo-600 hover:text-indigo-500">
                    <Coffee className="h-4 w-4 mr-1" />
                    Share Event
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}