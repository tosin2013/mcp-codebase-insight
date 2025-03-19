import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ChevronLeft, ChevronRight, CheckCircle, XCircle } from 'lucide-react';
import { Lesson, Module, getLearningPathWithModules, updateLessonProgress } from '../../types/learning-path';

interface LessonPageProps {}

interface RouteParams {
  slug: string;
  moduleId: string;
  lessonId: string;
}

export function LessonPage({}: LessonPageProps): JSX.Element {
  const { slug, moduleId, lessonId } = useParams<RouteParams>();
  const navigate = useNavigate();
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [module, setModule] = useState<Module | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [completed, setCompleted] = useState<boolean>(false);

  useEffect(() => {
    async function loadLessonData() {
      try {
        if (!slug || !moduleId || !lessonId) return;

        const pathData = await getLearningPathWithModules(slug);
        const foundModule = pathData.modules.find((m: Module) => m.id === moduleId);
        if (!foundModule) {
          throw new Error('Module not found');
        }
        setModule(foundModule);

        const foundLesson = foundModule.lessons?.find((l: Lesson) => l.id === lessonId);
        if (!foundLesson) {
          throw new Error('Lesson not found');
        }
        setLesson(foundLesson);
        setCompleted(foundLesson.progress?.completed || false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load lesson');
      } finally {
        setLoading(false);
      }
    }

    loadLessonData();
  }, [slug, moduleId, lessonId]);

  const handleComplete = async (): Promise<void> => {
    try {
      if (!lesson) return;
      await updateLessonProgress(lesson.id, { completed: !completed });
      setCompleted(!completed);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update lesson progress');
    }
  };

  const navigateToLesson = (targetLessonId: string): void => {
    navigate(`/learn/${slug}/modules/${moduleId}/lessons/${targetLessonId}`);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error || !lesson || !module) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
        <p className="text-gray-600">{error || 'Lesson not found'}</p>
      </div>
    );
  }

  const sortedLessons = module.lessons?.sort((a: Lesson, b: Lesson) => a.order_index - b.order_index) || [];
  const currentIndex = sortedLessons.findIndex((l: Lesson) => l.id === lessonId);
  const prevLesson = currentIndex > 0 ? sortedLessons[currentIndex - 1] : null;
  const nextLesson = currentIndex < sortedLessons.length - 1 ? sortedLessons[currentIndex + 1] : null;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Breadcrumb */}
      <nav className="flex mb-8" aria-label="Breadcrumb">
        <ol className="flex items-center space-x-2">
          <li>
            <a href="/learn" className="text-gray-500 hover:text-gray-700">Learning Paths</a>
          </li>
          <ChevronRight className="h-4 w-4 text-gray-400" />
          <li>
            <a href={`/learn/${slug}`} className="text-gray-500 hover:text-gray-700">{module.title}</a>
          </li>
          <ChevronRight className="h-4 w-4 text-gray-400" />
          <li className="text-gray-900 font-medium">{lesson.title}</li>
        </ol>
      </nav>

      {/* Lesson Content */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">{lesson.title}</h1>
        {lesson.video_url && (
          <div className="aspect-w-16 aspect-h-9 mb-6">
            <iframe src={lesson.video_url} title="Video Player" frameBorder="0" allowFullScreen></iframe>
          </div>
        )}
        <div className="prose prose-indigo" dangerouslySetInnerHTML={{ __html: lesson.content }}></div>
      </div>

      {/* Navigation & Completion */}
      <div className="flex justify-between items-center">
        <div>
          {prevLesson && (
            <button
              onClick={() => navigateToLesson(prevLesson.id)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              <ChevronLeft className="h-5 w-5 mr-2" />
              Previous Lesson
            </button>
          )}
        </div>
        <button
          onClick={handleComplete}
          className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
            completed
              ? 'bg-green-600 text-white hover:bg-green-700'
              : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
        >
          {completed ? (
            <>
              <XCircle className="h-5 w-5 mr-2" />
              Mark Incomplete
            </>
          ) : (
            <>
              <CheckCircle className="h-5 w-5 mr-2" />
              Mark Complete
            </>
          )}
        </button>
        <div>
          {nextLesson && (
            <button
              onClick={() => navigateToLesson(nextLesson.id)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Next Lesson
              <ChevronRight className="h-5 w-5 ml-2" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}