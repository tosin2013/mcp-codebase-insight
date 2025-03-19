import React from 'react';
import { Play, BookOpen, BarChart } from 'lucide-react';
import type { LearningPath } from '../../types';

interface LearningPathsProps {
  paths: LearningPath[];
}

function getDifficultyColor(difficulty: string) {
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
}

export function LearningPaths({ paths }: LearningPathsProps) {
  return (
    <div className="bg-white py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Popular Learning Paths
          </h2>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
            Curated video content to help you master new technologies and advance your career.
          </p>
        </div>

        <div className="mt-12 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {paths.map((path) => (
            <div
              key={path.id}
              className="flex flex-col bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
            >
              <div className="flex-1 p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-900">{path.title}</h3>
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(path.difficulty)}`}>
                    {path.difficulty.charAt(0).toUpperCase() + path.difficulty.slice(1)}
                  </span>
                </div>

                <p className="text-base text-gray-500 mb-4">
                  {path.description}
                </p>

                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-500">
                    <Play className="h-4 w-4 mr-2" />
                    {path.videos?.length || 0} Videos
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <BookOpen className="h-4 w-4 mr-2" />
                    {path.category}
                  </div>
                  <div className="flex items-center text-sm text-gray-500">
                    <BarChart className="h-4 w-4 mr-2" />
                    {path.difficulty.charAt(0).toUpperCase() + path.difficulty.slice(1)} Level
                  </div>
                </div>
              </div>

              <div className="px-6 py-4 bg-gray-50 border-t border-gray-100">
                <a
                  href={`/learn/${path.id}`}
                  className="text-base font-medium text-indigo-600 hover:text-indigo-500"
                >
                  Start Learning →
                </a>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}