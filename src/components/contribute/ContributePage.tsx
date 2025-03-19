import React, { useState } from 'react';
import { 
  GitBranch, Star, Users, Code, Award, 
  Clock, Tag, ExternalLink, Search, Filter,
  MessageSquare, ThumbsUp, PlusCircle, Rocket
} from 'lucide-react';
import { ProjectCard } from './ProjectCard';
import { ChallengeCard } from './ChallengeCard';
import { CollaborationBoard } from './CollaborationBoard';

interface OpenSourceProject {
  id: string;
  title: string;
  description: string;
  repository: string;
  maintainer: string;
  maintainerAvatar: string;
  tags: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  languages: string[];
  stars: number;
  forks: number;
  issues: number;
  lastUpdated: string;
}

interface Challenge {
  id: string;
  title: string;
  description: string;
  startDate: string;
  endDate: string;
  participants: number;
  prize: string;
  sponsor: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  tags: string[];
  status: 'upcoming' | 'active' | 'completed';
}

const projects: OpenSourceProject[] = [
  {
    id: '1',
    title: 'React Component Library',
    description: 'A collection of reusable React components with TypeScript support and comprehensive documentation.',
    repository: 'https://github.com/org/react-components',
    maintainer: 'Sarah Chen',
    maintainerAvatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    tags: ['react', 'typescript', 'ui-library'],
    difficulty: 'intermediate',
    languages: ['TypeScript', 'React', 'CSS'],
    stars: 245,
    forks: 45,
    issues: 12,
    lastUpdated: '2024-01-15'
  },
  {
    id: '2',
    title: 'Cloud Infrastructure Templates',
    description: 'Collection of Infrastructure as Code templates for AWS, Azure, and GCP using Terraform.',
    repository: 'https://github.com/org/cloud-templates',
    maintainer: 'Michael Torres',
    maintainerAvatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?ixlib=rb-1.2.1&auto=format&fit=facearea&facepad=2&w=256&h=256&q=80',
    tags: ['infrastructure', 'terraform', 'cloud'],
    difficulty: 'advanced',
    languages: ['HCL', 'YAML', 'Shell'],
    stars: 567,
    forks: 89,
    issues: 23,
    lastUpdated: '2024-01-10'
  }
];

const challenges: Challenge[] = [
  {
    id: '1',
    title: 'Build a Real-time Chat Application',
    description: 'Create a real-time chat application using WebSocket technology and modern frontend frameworks.',
    startDate: '2024-02-01',
    endDate: '2024-02-28',
    participants: 156,
    prize: '$1,000 in Cloud Credits',
    sponsor: 'TechCorp',
    difficulty: 'intermediate',
    tags: ['websocket', 'react', 'node.js'],
    status: 'upcoming'
  },
  {
    id: '2',
    title: 'Serverless API Challenge',
    description: 'Build a scalable API using serverless technologies. Focus on performance and cost optimization.',
    startDate: '2024-03-01',
    endDate: '2024-03-31',
    participants: 89,
    prize: '$2,000 + Mentorship',
    sponsor: 'CloudScale',
    difficulty: 'advanced',
    tags: ['serverless', 'aws', 'api'],
    status: 'upcoming'
  }
];

export function ContributePage() {
  const [activeTab, setActiveTab] = useState<'projects' | 'challenges' | 'board'>('projects');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('all');

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-indigo-700 text-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-3xl font-extrabold sm:text-4xl">
              Contribute & Collaborate
            </h1>
            <p className="mt-3 text-xl text-indigo-200">
              Join open-source projects, participate in challenges, and build together
            </p>
          </div>

          {/* Quick Stats */}
          <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <GitBranch className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">50+</div>
                  <div className="text-indigo-200">Active Projects</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Award className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">$5K+</div>
                  <div className="text-indigo-200">in Prizes</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Users className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">1,000+</div>
                  <div className="text-indigo-200">Contributors</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Navigation and Search */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search projects, challenges, or skills..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => setActiveTab('projects')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'projects'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <GitBranch className="h-5 w-5 inline-block mr-2" />
                Projects
              </button>
              <button
                onClick={() => setActiveTab('challenges')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'challenges'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Award className="h-5 w-5 inline-block mr-2" />
                Challenges
              </button>
              <button
                onClick={() => setActiveTab('board')}
                className={`px-4 py-2 rounded-md ${
                  activeTab === 'board'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <MessageSquare className="h-5 w-5 inline-block mr-2" />
                Board
              </button>
            </div>
          </div>
        </div>

        {/* Content Sections */}
        {activeTab === 'projects' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Open Source Projects</h2>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
                <PlusCircle className="h-4 w-4 mr-2" />
                Submit Project
              </button>
            </div>
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {projects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'challenges' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Coding Challenges</h2>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
                <Rocket className="h-4 w-4 mr-2" />
                Create Challenge
              </button>
            </div>
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {challenges.map((challenge) => (
                <ChallengeCard key={challenge.id} challenge={challenge} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'board' && (
          <CollaborationBoard />
        )}
      </div>
    </div>
  );
}