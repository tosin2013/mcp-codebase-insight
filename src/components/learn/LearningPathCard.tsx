import React from 'react';
import { Play, Clock, Users, Star, BookOpen } from 'lucide-react';
import type { LearningPath } from '../../types';

interface LearningPathCardProps {
  path: LearningPath;
}

export function LearningPathCard({ path }: LearningPathCardProps) {
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
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-start">
          <h3 className="text-lg font-medium text-gray-900">{path.title}</h3>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(path.difficulty)}`}>
            {path.difficulty.charAt(0).toUpperCase() + path.difficulty.slice(1)}
          </span>
        </div>

        <p className="mt-2 text-sm text-gray-500">{path.description}</p>

        <div className="mt-4 flex items-center justify-between text-sm text-gray-500">
          <div className="flex space-x-4">
            <span className="flex items-center">
              <Play className="h-4 w-4 mr-1" />
              {path.videos?.length || 0} videos
            </span>
            <span className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              20 hours
            </span>
            <span className="flex items-center">
              <Users className="h-4 w-4 mr-1" />
              1.2k learners
            </span>
          </div>
          <div className="flex items-center">
            <Star className="h-4 w-4 text-yellow-400" />
            <span className="ml-1">4.8</span>
          </div>
        </div>

        <div className="mt-6 flex justify-between items-center">
          <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
            <BookOpen className="h-4 w-4 mr-2" />
            Start Learning
          </button>
          <button className="inline-flex items-center text-sm text-indigo-600 hover:text-indigo-500">
            View Curriculum
          </button>
        </div>
      </div>
    </div>
  );
}