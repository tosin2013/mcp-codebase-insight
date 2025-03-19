import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronRight, BookOpen, Clock, Users, Star, CheckCircle } from 'lucide-react';
import { LearningPath, Module, PathProgress, getLearningPathWithModules, getPathProgress, enrollInPath } from '../../types/learning-path';

interface LearningPathPageProps {
  onModuleSelect?: (moduleId: string) => void;
}

interface RouteParams extends Record<string, string | undefined> {
  slug: string;
}

export function LearningPathPage({ onModuleSelect }: LearningPathPageProps): JSX.Element {
  const { slug } = useParams<RouteParams>();
  const navigate = useNavigate();
  const [path, setPath] = useState<(LearningPath & { modules: Module[] }) | null>(null);
  const [progress, setProgress] = useState<PathProgress | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadPathData() {
      try {
        if (!slug) return;
        
        const pathData = await getLearningPathWithModules(slug);
        setPath(pathData);
        
        const progressData = await getPathProgress(pathData.id);
        setProgress(progressData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load learning path');
      } finally {
        setLoading(false);
      }
    }

    loadPathData();
  }, [slug]);

  const handleEnroll = async (): Promise<void> => {
    try {
      if (!path) return;
      await enrollInPath(path.id);
      // Refresh progress after enrollment
      const progressData = await getPathProgress(path.id);
      setProgress(progressData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to enroll in path');
    }
  };

  const handleModuleClick = (moduleId: string): void => {
    if (onModuleSelect) {
      onModuleSelect(moduleId);
    } else {
      navigate(`/learn/${slug}/modules/${moduleId}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !path) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
        <p className="text-gray-600">{error || 'Learning path not found'}</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex mb-8" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-2">
          <li>
            <a href="/learn" className="text-gray-500 hover:text-gray-700">Learning Paths</a>
          </li>
          <ChevronRight className="h-4 w-4 text-gray-400" />
          <li className="text-gray-900 font-medium">{path.title}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="mb-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{path.title}</h1>
            <p className="text-lg text-gray-600 mb-4">{path.description}</p>
          </div>
          <span
            className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              path.difficulty === 'beginner'
                ? 'bg-green-100 text-green-800'
                : path.difficulty === 'intermediate'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {path.difficulty.charAt(0).toUpperCase() + path.difficulty.slice(1)}
          </span>
        </div>

        {/* Stats */}
        <div className="flex items-center space-x-6 text-sm text-gray-500">
          <span className="flex items-center">
            <Clock className="h-4 w-4 mr-1" />
            {path.estimated_hours} hours
          </span>
          <span className="flex items-center">
            <Users className="h-4 w-4 mr-1" />
            {path.modules.reduce((sum: number, module: Module) => sum + (module.lessons?.length || 0), 0)} lessons
          </span>
          <span className="flex items-center">
            <Star className="h-4 w-4 text-yellow-400 mr-1" />
            4.8 average rating
          </span>
          {progress && (
            <span className="flex items-center">
              <CheckCircle className="h-4 w-4 text-green-500 mr-1" />
              {progress.progress_percentage}% complete
            </span>
          )}
        </div>
      </div>

      {/* Prerequisites and Objectives */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Prerequisites</h2>
          <ul className="list-disc list-inside text-gray-600">
            {path.prerequisites.map((prereq: string, index: number) => (
              <li key={index}>{prereq}</li>
            ))}
          </ul>
        </div>
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Learning Objectives</h2>
          <ul className="list-disc list-inside text-gray-600">
            {path.learning_objectives.map((objective: string, index: number) => (
              <li key={index}>{objective}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Modules */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-gray-900 mb-6">Course Content</h2>
        <div className="space-y-4">
          {path.modules
            .sort((a: Module, b: Module) => a.order_index - b.order_index)
            .map((module: Module) => (
              <div
                key={module.id}
                className="bg-white rounded-lg shadow-sm overflow-hidden hover:shadow-md transition-shadow"
              >
                <button
                  onClick={() => handleModuleClick(module.id)}
                  className="w-full text-left p-6"
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h3 className="text-lg font-medium text-gray-900">{module.title}</h3>
                      <p className="mt-1 text-sm text-gray-500">{module.description}</p>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="text-sm text-gray-500">
                        {module.lessons?.length || 0} lessons
                      </span>
                      <ChevronRight className="h-5 w-5 text-gray-400" />
                    </div>
                  </div>
                </button>
              </div>
            ))}
        </div>
      </div>

      {/* Enroll Button */}
      {!progress && (
        <div className="flex justify-center">
          <button
            onClick={handleEnroll}
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <BookOpen className="h-5 w-5 mr-2" />
            Enroll in Course
          </button>
        </div>
      )}
    </div>
  );
}