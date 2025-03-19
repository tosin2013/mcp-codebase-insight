import React from 'react';
import { ExternalLink, Github, Edit, Trash2, Users } from 'lucide-react';
import type { Project } from '../../types';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      {project.images[0] && (
        <img
          src={project.images[0]}
          alt={project.title}
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-6">
        <h3 className="text-lg font-medium text-gray-900">{project.title}</h3>
        <p className="mt-2 text-sm text-gray-500">{project.description}</p>
        
        <div className="mt-4 flex flex-wrap gap-2">
          {project.technologies.map((tech) => (
            <span
              key={tech}
              className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
            >
              {tech}
            </span>
          ))}
        </div>

        <div className="mt-4 flex items-center text-sm text-gray-500">
          <Users className="h-4 w-4 mr-1" />
          <span>{project.collaborators.length} collaborators</span>
        </div>

        <div className="mt-4 flex justify-between items-center">
          <div className="flex space-x-2">
            {project.url && (
              <a
                href={project.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-indigo-600"
              >
                <ExternalLink className="h-5 w-5" />
              </a>
            )}
            {project.githubUrl && (
              <a
                href={project.githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-indigo-600"
              >
                <Github className="h-5 w-5" />
              </a>
            )}
          </div>
          <div className="flex space-x-2">
            <button className="text-gray-400 hover:text-indigo-600">
              <Edit className="h-5 w-5" />
            </button>
            <button className="text-gray-400 hover:text-red-600">
              <Trash2 className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}