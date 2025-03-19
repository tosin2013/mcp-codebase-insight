import React, { useState } from 'react';
import { 
  Briefcase, Award, Users, Code, Book, Star, 
  GitBranch, ExternalLink, MessageSquare, HelpCircle,
  PlusCircle, Edit, Trash2, Share2, Download
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';
import { PortfolioAssessment } from './PortfolioAssessment';
import { ProjectCard } from './ProjectCard';
import { SkillCard } from './SkillCard';
import { CollaborationCard } from './CollaborationCard';
import { HelpRequest } from './HelpRequest';
import type { Project, Skill, Collaboration } from '../../types';

export function PortfolioPage() {
  const { user } = useAuth();
  const [showAssessment, setShowAssessment] = useState(false);
  const [showHelpRequest, setShowHelpRequest] = useState(false);
  const [activeTab, setActiveTab] = useState<'projects' | 'skills' | 'collaborations'>('projects');

  // Sample data - in a real app, this would come from your database
  const projects: Project[] = [
    {
      id: '1',
      title: 'E-commerce Platform',
      description: 'A full-stack e-commerce solution built with React and Node.js',
      technologies: ['React', 'Node.js', 'PostgreSQL', 'Redis'],
      url: 'https://example.com/project',
      githubUrl: 'https://github.com/user/project',
      images: [
        'https://images.unsplash.com/photo-1557821552-17105176677c?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80'
      ],
      collaborators: ['Emily Johnson', 'David Park'],
      startDate: new Date('2023-09-01'),
      endDate: new Date('2023-12-31')
    }
  ];

  const skills: Skill[] = [
    {
      name: 'React',
      level: 'advanced',
      endorsements: 15,
      verified: true
    },
    {
      name: 'Node.js',
      level: 'intermediate',
      endorsements: 8,
      verified: true
    }
  ];

  const collaborations: Collaboration[] = [
    {
      id: '1',
      projectId: '1',
      userId: 'user1',
      role: 'Frontend Developer',
      status: 'completed',
      startDate: new Date('2023-09-01'),
      endDate: new Date('2023-12-31')
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-indigo-700 text-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-3xl font-extrabold sm:text-4xl">
              Your Professional Portfolio
            </h1>
            <p className="mt-3 text-xl text-indigo-200">
              Showcase your skills, projects, and achievements
            </p>
          </div>

          {/* Quick Stats */}
          <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-4">
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Briefcase className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">{projects.length}</div>
                  <div className="text-indigo-200">Projects</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Code className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">{skills.length}</div>
                  <div className="text-indigo-200">Skills</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Users className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">{collaborations.length}</div>
                  <div className="text-indigo-200">Collaborations</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Award className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">12</div>
                  <div className="text-indigo-200">Endorsements</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 mb-8">
          <button
            onClick={() => setShowAssessment(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
          >
            <HelpCircle className="h-4 w-4 mr-2" />
            Portfolio Assessment
          </button>
          <button
            onClick={() => setShowHelpRequest(true)}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700"
          >
            <MessageSquare className="h-4 w-4 mr-2" />
            Ask for Help
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-purple-600 hover:bg-purple-700">
            <Share2 className="h-4 w-4 mr-2" />
            Invite Reviewer
          </button>
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700">
            <Download className="h-4 w-4 mr-2" />
            Export Portfolio
          </button>
        </div>

        {/* Portfolio Navigation */}
        <div className="flex border-b border-gray-200 mb-8">
          <button
            onClick={() => setActiveTab('projects')}
            className={`px-4 py-2 border-b-2 font-medium text-sm ${
              activeTab === 'projects'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Briefcase className="h-4 w-4 inline-block mr-2" />
            Projects
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`px-4 py-2 border-b-2 font-medium text-sm ${
              activeTab === 'skills'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Code className="h-4 w-4 inline-block mr-2" />
            Skills
          </button>
          <button
            onClick={() => setActiveTab('collaborations')}
            className={`px-4 py-2 border-b-2 font-medium text-sm ${
              activeTab === 'collaborations'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Users className="h-4 w-4 inline-block mr-2" />
            Collaborations
          </button>
        </div>

        {/* Content Sections */}
        {activeTab === 'projects' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Projects</h2>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
                <PlusCircle className="h-4 w-4 mr-2" />
                Add Project
              </button>
            </div>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {projects.map((project) => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'skills' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Skills</h2>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
                <PlusCircle className="h-4 w-4 mr-2" />
                Add Skill
              </button>
            </div>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {skills.map((skill) => (
                <SkillCard key={skill.name} skill={skill} />
              ))}
            </div>
          </div>
        )}

        {activeTab === 'collaborations' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Collaborations</h2>
              <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
                <PlusCircle className="h-4 w-4 mr-2" />
                Add Collaboration
              </button>
            </div>
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {collaborations.map((collaboration) => (
                <CollaborationCard key={collaboration.id} collaboration={collaboration} />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showAssessment && user && (
        <PortfolioAssessment 
          onClose={() => setShowAssessment(false)} 
          userId={user.id}
        />
      )}

      {showHelpRequest && (
        <HelpRequest onClose={() => setShowHelpRequest(false)} />
      )}
    </div>
  );
}