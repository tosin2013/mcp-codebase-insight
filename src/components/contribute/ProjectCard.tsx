import React from 'react';
import { GitBranch, Star, GitFork, AlertCircle, ExternalLink } from 'lucide-react';

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

interface ProjectCardProps {
  project: OpenSourceProject;
}

export function ProjectCard({ project }: ProjectCardProps) {
  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{project.title}</h3>
          <div className="mt-1 flex items-center">
            <img
              src={project.maintainerAvatar}
              alt={project.maintainer}
              className="h-6 w-6 rounded-full"
            />
            <span className="ml-2 text-sm text-gray-500">{project.maintainer}</span>
          </div>
        </div>
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(project.difficulty)}`}>
          {project.difficulty.charAt(0).toUpperCase() + project.difficulty.slice(1)}
        </span>
      </div>

      <p className="mt-3 text-sm text-gray-500">{project.description}</p>

      <div className="mt-4">
        <div className="flex flex-wrap gap-2">
          {project.languages.map((language) => (
            <span
              key={language}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
            >
              {language}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <div className="flex flex-wrap gap-2">
          {project.tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
            >
              #{tag}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
        <div className="flex space-x-4">
          <span className="flex items-center">
            <Star className="h-4 w-4 mr-1" />
            {project.stars}
          </span>
          <span className="flex items-center">
            <GitFork className="h-4 w-4 mr-1" />
            {project.forks}
          </span>
          <span className="flex items-center">
            <AlertCircle className="h-4 w-4 mr-1" />
            {project.issues}
          </span>
        </div>
        <span>Updated {project.lastUpdated}</span>
      </div>

      <div className="mt-4 flex justify-between">
        <a
          href={project.repository}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
        >
          <GitBranch className="h-4 w-4 mr-2" />
          View Repository
        </a>
        <button className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
          <ExternalLink className="h-4 w-4 mr-2" />
          Quick Start
        </button>
      </div>
    </div>
  );
}