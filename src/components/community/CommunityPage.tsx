import React, { useState } from 'react';
import { MessageSquare, Users, Calendar, Award, Bookmark, ThumbsUp, Share2, Flag, Search } from 'lucide-react';

interface ForumPost {
  id: string;
  title: string;
  author: {
    name: string;
    avatar: string;
    role: string;
  };
  category: string;
  content: string;
  likes: number;
  replies: number;
  timestamp: string;
  tags: string[];
}

interface CommunityMember {
  id: string;
  name: string;
  role: string;
  avatar: string;
  contributions: number;
  badges: string[];
  specialization: string;
}

const forumPosts: ForumPost[] = [
  {
    id: '1',
    title: 'Best practices for learning React in 2024',
    author: {
      name: 'Sarah Chen',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
      role: 'Moderator'
    },
    category: 'Frontend Development',
    content: "I have been mentoring new React developers, and I wanted to share some tips that have helped my students...",
    likes: 45,
    replies: 23,
    timestamp: '2 hours ago',
    tags: ['react', 'javascript', 'frontend']
  },
  {
    id: '2',
    title: 'AWS Certification Study Group',
    author: {
      name: 'Michael Torres',
      avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
      role: 'Cloud Expert'
    },
    category: 'Cloud Computing',
    content: "Looking to form a study group for the AWS Solutions Architect certification. We can meet weekly to discuss topics and practice exam questions.",
    likes: 32,
    replies: 15,
    timestamp: '5 hours ago',
    tags: ['aws', 'cloud', 'certification']
  }
];

const featuredMembers: CommunityMember[] = [
  {
    id: '1',
    name: 'Emily Johnson',
    role: 'Frontend Developer',
    avatar: 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    contributions: 156,
    badges: ['Top Contributor', 'React Expert'],
    specialization: 'React & TypeScript'
  },
  {
    id: '2',
    name: 'David Park',
    role: 'DevOps Engineer',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    contributions: 89,
    badges: ['AWS Certified', 'Mentor'],
    specialization: 'Cloud Infrastructure'
  }
];

export function CommunityPage() {
  const [activeTab, setActiveTab] = useState<'discussions' | 'members' | 'events'>('discussions');
  const [searchTerm, setSearchTerm] = useState('');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Rest of the component remains the same */}
      {/* Hero Section */}
      <div className="bg-indigo-700 text-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-3xl font-extrabold sm:text-4xl">
              Welcome to the TechPath Community
            </h1>
            <p className="mt-3 text-xl text-indigo-200">
              Connect, learn, and grow with fellow tech enthusiasts
            </p>
          </div>

          {/* Community Stats */}
          <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-indigo-800 rounded-lg p-5 text-center">
              <div className="flex justify-center">
                <Users className="h-8 w-8 text-indigo-400" />
              </div>
              <div className="mt-3">
                <div className="text-3xl font-bold">5,000+</div>
                <div className="text-indigo-200">Active Members</div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5 text-center">
              <div className="flex justify-center">
                <MessageSquare className="h-8 w-8 text-indigo-400" />
              </div>
              <div className="mt-3">
                <div className="text-3xl font-bold">10,000+</div>
                <div className="text-indigo-200">Discussions</div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5 text-center">
              <div className="flex justify-center">
                <Award className="h-8 w-8 text-indigo-400" />
              </div>
              <div className="mt-3">
                <div className="text-3xl font-bold">2,500+</div>
                <div className="text-indigo-200">Success Stories</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Search and Navigation */}
        <div className="flex flex-col sm:flex-row justify-between items-center mb-8">
          <div className="flex space-x-4 mb-4 sm:mb-0">
            <button
              onClick={() => setActiveTab('discussions')}
              className={`px-4 py-2 rounded-md ${
                activeTab === 'discussions'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <MessageSquare className="h-5 w-5 inline-block mr-2" />
              Discussions
            </button>
            <button
              onClick={() => setActiveTab('members')}
              className={`px-4 py-2 rounded-md ${
                activeTab === 'members'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Users className="h-5 w-5 inline-block mr-2" />
              Members
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
          <div className="relative">
            <input
              type="text"
              placeholder="Search community..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full sm:w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
            />
            <Search className="h-5 w-5 text-gray-400 absolute left-3 top-2.5" />
          </div>
        </div>

        {/* Featured Members */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Featured Community Members</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredMembers.map((member) => (
              <div key={member.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                <img
                  src={member.avatar}
                  alt={member.name}
                  className="h-12 w-12 rounded-full"
                />
                <div>
                  <h3 className="text-sm font-medium text-gray-900">{member.name}</h3>
                  <p className="text-sm text-gray-500">{member.role}</p>
                  <div className="mt-1 flex space-x-2">
                    {member.badges.map((badge) => (
                      <span
                        key={badge}
                        className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800"
                      >
                        {badge}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Forum Posts */}
        <div className="space-y-6">
          {forumPosts.map((post) => (
            <div key={post.id} className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <img
                    src={post.author.avatar}
                    alt={post.author.name}
                    className="h-10 w-10 rounded-full"
                  />
                  <div>
                    <h3 className="text-sm font-medium text-gray-900">{post.author.name}</h3>
                    <p className="text-sm text-gray-500">{post.author.role}</p>
                  </div>
                </div>
                <span className="text-sm text-gray-500">{post.timestamp}</span>
              </div>
              <h2 className="mt-4 text-xl font-semibold text-gray-900">{post.title}</h2>
              <p className="mt-2 text-gray-600">{post.content}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {post.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
              <div className="mt-6 flex items-center space-x-4 text-gray-500">
                <button className="flex items-center space-x-1 hover:text-indigo-600">
                  <ThumbsUp className="h-4 w-4" />
                  <span>{post.likes}</span>
                </button>
                <button className="flex items-center space-x-1 hover:text-indigo-600">
                  <MessageSquare className="h-4 w-4" />
                  <span>{post.replies}</span>
                </button>
                <button className="flex items-center space-x-1 hover:text-indigo-600">
                  <Share2 className="h-4 w-4" />
                  <span>Share</span>
                </button>
                <button className="flex items-center space-x-1 hover:text-indigo-600">
                  <Bookmark className="h-4 w-4" />
                  <span>Save</span>
                </button>
                <button className="flex items-center space-x-1 hover:text-red-600">
                  <Flag className="h-4 w-4" />
                  <span>Report</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}