import React, { useState, useEffect } from 'react';
import { 
  BookOpen, Code, Award, Brain, Search, Filter,
  Rocket, Star, Clock, Users, Play, CheckCircle,
  BarChart, Target, Briefcase
} from 'lucide-react';
import { supabase } from '../../lib/supabase';
import { LearningPathCard } from './LearningPathCard';
import { SkillAssessment } from './SkillAssessment';
import { CertificationTrack } from './CertificationTrack';
import type { LearningPath } from '../../types';

export function LearnPage() {
  const [showAssessment, setShowAssessment] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [learningPaths, setLearningPaths] = useState<LearningPath[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchLearningPaths() {
      try {
        setLoading(true);
        setError(null);

        const { data: paths, error: fetchError } = await supabase
          .from('learning_paths')
          .select(`
            *,
            videos:learning_path_videos(*)
          `)
          .order('created_at', { ascending: false });

        if (fetchError) throw fetchError;

        // Transform the data to match our types
        const formattedPaths: LearningPath[] = paths.map(path => ({
          id: path.id,
          title: path.title,
          description: path.description,
          category: path.category,
          difficulty: path.difficulty,
          createdAt: new Date(path.created_at),
          updatedAt: new Date(path.updated_at),
          videos: path.videos.map((video: any) => ({
            id: video.id,
            pathId: video.path_id,
            title: video.title,
            description: video.description,
            youtubeUrl: video.youtube_url,
            orderIndex: video.order_index,
            createdAt: new Date(video.created_at),
            updatedAt: new Date(video.updated_at)
          }))
        }));

        setLearningPaths(formattedPaths);
      } catch (err) {
        console.error('Error fetching learning paths:', err);
        setError('Failed to load learning paths. Please try again later.');
      } finally {
        setLoading(false);
      }
    }

    fetchLearningPaths();
  }, []);

  // Filter learning paths based on search and filters
  const filteredPaths = learningPaths.filter(path => {
    const matchesSearch = 
      path.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      path.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesCategory = selectedCategory === 'all' || path.category === selectedCategory;
    const matchesDifficulty = selectedDifficulty === 'all' || path.difficulty === selectedDifficulty;

    return matchesSearch && matchesCategory && matchesDifficulty;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-indigo-700 text-white">
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-3xl font-extrabold sm:text-4xl">
              Learn & Grow Your Skills
            </h1>
            <p className="mt-3 text-xl text-indigo-200">
              Curated learning paths and resources to advance your tech career
            </p>
          </div>

          {/* Quick Stats */}
          <div className="mt-10 grid grid-cols-1 gap-5 sm:grid-cols-4">
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <BookOpen className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">{learningPaths.length}</div>
                  <div className="text-indigo-200">Learning Paths</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Code className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">
                    {learningPaths.reduce((total, path) => total + (path.videos?.length || 0), 0)}
                  </div>
                  <div className="text-indigo-200">Video Lessons</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Award className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">25+</div>
                  <div className="text-indigo-200">Certifications</div>
                </div>
              </div>
            </div>
            <div className="bg-indigo-800 rounded-lg p-5">
              <div className="flex items-center">
                <Users className="h-6 w-6 text-indigo-400" />
                <div className="ml-3">
                  <div className="text-2xl font-bold">50K+</div>
                  <div className="text-indigo-200">Active Learners</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* AI Assessment CTA */}
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-xl overflow-hidden mb-8">
          <div className="px-6 py-8 sm:p-10 sm:pb-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-bold text-white">AI-Powered Skill Assessment</h3>
                <p className="mt-2 text-lg text-purple-100">
                  Get personalized learning recommendations based on your current skills and career goals
                </p>
              </div>
              <Brain className="h-12 w-12 text-purple-200" />
            </div>
            <div className="mt-6">
              <button
                onClick={() => setShowAssessment(true)}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-purple-600 bg-white hover:bg-purple-50 shadow-sm"
              >
                <Target className="h-5 w-5 mr-2" />
                Start Assessment
              </button>
            </div>
          </div>
          <div className="px-6 pt-6 pb-8 bg-purple-700 bg-opacity-50 sm:px-10">
            <div className="flex items-center">
              <CheckCircle className="h-5 w-5 text-purple-200" />
              <p className="ml-3 text-sm text-purple-100">
                Identify skill gaps and growth opportunities
              </p>
            </div>
            <div className="mt-4 flex items-center">
              <BarChart className="h-5 w-5 text-purple-200" />
              <p className="ml-3 text-sm text-purple-100">
                Track your progress and learning velocity
              </p>
            </div>
            <div className="mt-4 flex items-center">
              <Briefcase className="h-5 w-5 text-purple-200" />
              <p className="ml-3 text-sm text-purple-100">
                Get matched with relevant job opportunities
              </p>
            </div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search learning paths..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
            <div className="flex gap-4">
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="block pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="all">All Categories</option>
                <option value="Web Development">Web Development</option>
                <option value="Cloud Computing">Cloud Computing</option>
                <option value="DevOps">DevOps</option>
                <option value="Mobile Development">Mobile Development</option>
                <option value="AI & Machine Learning">AI & Machine Learning</option>
              </select>
              <select
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
                className="block pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="all">All Levels</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </div>
        </div>

        {/* Learning Paths */}
        <div className="space-y-8">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-gray-900">Featured Learning Paths</h2>
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
              <Rocket className="h-4 w-4 mr-2" />
              View All Paths
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border-l-4 border-red-400 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <span className="text-red-400">⚠</span>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {loading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {filteredPaths.map((path) => (
                <LearningPathCard key={path.id} path={path} />
              ))}
            </div>
          )}
        </div>

        {/* Certification Tracks */}
        <div className="mt-12">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Certification Tracks</h2>
            <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
              <Award className="h-4 w-4 mr-2" />
              View All Certifications
            </button>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <CertificationTrack
              title="AWS Cloud Practitioner"
              description="Start your cloud journey with AWS fundamentals"
              duration="3 months"
              level="Beginner"
              examCode="CLF-C01"
              price="$100"
            />
            <CertificationTrack
              title="React Developer"
              description="Master React and modern frontend development"
              duration="4 months"
              level="Intermediate"
              examCode="RD-201"
              price="$150"
            />
            <CertificationTrack
              title="Full Stack Engineer"
              description="Become a complete full-stack developer"
              duration="6 months"
              level="Advanced"
              examCode="FSE-301"
              price="$200"
            />
          </div>
        </div>
      </div>

      {/* Assessment Modal */}
      {showAssessment && (
        <SkillAssessment onClose={() => setShowAssessment(false)} />
      )}
    </div>
  );
}