import React, { useState, useEffect } from 'react';
import { X, Brain, ChevronRight, Target, Code, Briefcase, Award, Book, Rocket } from 'lucide-react';
import { supabase } from '../../lib/supabase';

interface SkillAssessmentProps {
  onClose: () => void;
  onComplete: (recommendations: any) => void;
}

export function SkillAssessment({ onClose, onComplete }: SkillAssessmentProps) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState({
    currentRole: '',
    yearsExperience: '',
    targetRole: '',
    interests: [] as string[], 
    skills: {
      frontend: [] as string[],
      backend: [] as string[],
      devops: [] as string[],
      cloud: [] as string[]
    },
    learningStyle: '',
    timeCommitment: ''
  });

  const [skillCategories, setSkillCategories] = useState<Record<string, string[]>>({});
  const [roleTargets, setRoleTargets] = useState<Array<{
    title: string;
    description: string;
    required_skills: { required: string[]; preferred: string[] };
  }>>([]);

  useEffect(() => {
    fetchSkillsAndRoles();
  }, []);

  async function fetchSkillsAndRoles() {
    try {
      // Fetch skill categories and skills
      const { data: categories, error: categoriesError } = await supabase
        .from('skill_categories')
        .select(`
          id,
          name,
          skills (
            name,
            level
          )
        `);

      if (categoriesError) throw categoriesError;

      // Transform into the format we need
      const formattedCategories: Record<string, string[]> = {};
      categories?.forEach(category => {
        formattedCategories[category.name.toLowerCase()] = 
          category.skills.map(skill => skill.name);
      });
      setSkillCategories(formattedCategories);

      // Fetch role targets
      const { data: roles, error: rolesError } = await supabase
        .from('role_targets')
        .select('*');

      if (rolesError) throw rolesError;
      setRoleTargets(roles);

    } catch (err) {
      console.error('Error fetching skills and roles:', err);
      setError('Failed to load skills and roles. Please try again.');
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (!formData.currentRole || !formData.yearsExperience || !formData.targetRole) {
        throw new Error('Please fill in all required fields');
      }
      
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) throw new Error('User not authenticated');

      const assessmentData = {
        user_id: user.id,
        assessment_data: {
          currentStatus: {
            role: formData.currentRole,
            yearsExperience: formData.yearsExperience
          },
          goals: {
            targetRole: formData.targetRole,
            interests: formData.interests
          },
          skills: formData.skills,
          learningStyle: formData.learningStyle,
          timeCommitment: formData.timeCommitment,
          metadata: {
            submittedFrom: window.location.pathname,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString()
          }
        },
        completed_at: new Date().toISOString()
      };

      const { error: logError } = await supabase
        .from('skill_assessments')
        .insert([assessmentData]);

      if (logError) throw logError;

      const recommendations = generateRecommendations(assessmentData.assessment_data);
      onComplete(recommendations);
      onClose();
    } catch (err) {
      console.error('Error submitting assessment:', err);
      setError(err instanceof Error ? err.message : 'Failed to submit assessment. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const generateRecommendations = (data: any) => {
    const recommendations = {
      learningPaths: [] as string[],
      projects: [] as string[],
      mentorship: [] as string[],
      certifications: [] as string[]
    };

    const targetRole = data.goals.targetRole;
    
    if (!targetRole) {
      return recommendations;
    }

    if (targetRole.toLowerCase().includes('frontend')) {
      recommendations.learningPaths.push('Frontend Development Mastery');
      recommendations.certifications.push('React Developer Certification');
    }

    if (targetRole.toLowerCase().includes('cloud')) {
      recommendations.learningPaths.push('Cloud Architecture Fundamentals');
      recommendations.certifications.push('AWS Solutions Architect');
    }

    // Add recommendations based on skill gaps
    const roleTarget = roleTargets.find(role => role.title === targetRole);
    if (roleTarget) {
      const requiredSkills = roleTarget.required_skills.required;
      const userSkills = Object.values(data.skills).flat();
      
      // Find missing required skills
      const missingSkills = requiredSkills.filter(skill => !userSkills.includes(skill));
      
      // Add learning paths for missing skills
      missingSkills.forEach(skill => {
        const category = Object.entries(skillCategories).find(([_, skills]) => 
          skills.includes(skill)
        )?.[0];
        
        if (category) {
          recommendations.learningPaths.push(`${skill} Fundamentals`);
        }
      });
    }
    return recommendations;
  };
  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-4xl w-full mx-4 overflow-hidden">
        <div className="px-6 py-4 bg-indigo-600 text-white flex justify-between items-center">
          <h3 className="text-lg font-medium flex items-center">
            <Brain className="h-5 w-5 mr-2" />
            AI-Powered Skill Assessment
          </h3>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="px-6 py-4 max-h-[80vh] overflow-y-auto">
          {error && (
            <div className="mb-4 bg-red-50 border-l-4 border-red-400 p-4">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div className="flex justify-between mb-8">
            {[1, 2, 3].map((s) => (
              <div
                key={s}
                className={`flex items-center ${
                  s < step ? 'text-indigo-600' : s === step ? 'text-gray-900' : 'text-gray-400'
                }`}
              >
                <div className={`flex items-center justify-center h-8 w-8 rounded-full border-2 ${
                  s < step ? 'border-indigo-600 bg-indigo-600 text-white' :
                  s === step ? 'border-gray-900' : 'border-gray-400'
                }`}>
                  {s}
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium">
                    {s === 1 ? 'Current Status' :
                     s === 2 ? 'Goals' : 'Skills'}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {step === 1 && (
            <div className="space-y-6">
              <div>
                <label htmlFor="currentRole" className="block text-sm font-medium text-gray-700">
                  Current Role
                </label>
                <select
                  id="currentRole"
                  value={formData.currentRole}
                  onChange={(e) => setFormData({ ...formData, currentRole: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option value="">Select your role</option>
                  <option value="frontend">Frontend Developer</option>
                  <option value="backend">Backend Developer</option>
                  <option value="fullstack">Full Stack Developer</option>
                  <option value="devops">DevOps Engineer</option>
                </select>
              </div>

              <div>
                <label htmlFor="yearsExperience" className="block text-sm font-medium text-gray-700">
                  Years of Experience
                </label>
                <select
                  id="yearsExperience"
                  value={formData.yearsExperience}
                  onChange={(e) => setFormData({ ...formData, yearsExperience: e.target.value })}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                >
                  <option value="">Select experience</option>
                  <option value="0-1">0-1 years</option>
                  <option value="1-3">1-3 years</option>
                  <option value="3-5">3-5 years</option>
                  <option value="5+">5+ years</option>
                </select>
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-6">
              <div>
                <label htmlFor="targetRole" className="block text-sm font-medium text-gray-700">
                  Target Role
                </label>
                <div className="mt-1 space-y-4">
                  {roleTargets.map((role) => (
                    <div key={role.title} className="relative flex items-start">
                      <div className="flex items-center h-5">
                        <input
                          type="radio"
                          name="targetRole"
                          value={role.title}
                          checked={formData.targetRole === role.title}
                          onChange={(e) => setFormData({ ...formData, targetRole: e.target.value })}
                          className="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500"
                        />
                      </div>
                      <div className="ml-3 text-sm">
                        <label className="font-medium text-gray-700">{role.title}</label>
                        <p className="text-gray-500">{role.description}</p>
                        <div className="mt-1">
                          <span className="text-xs font-medium text-gray-500">Required skills: </span>
                          {role.required_skills.required.map((skill, index) => (
                            <span key={skill} className="text-xs text-indigo-600">
                              {skill}{index < role.required_skills.required.length - 1 ? ', ' : ''}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">
                  Areas of Interest
                </label>
                <div className="mt-2 space-y-2">
                  {['Web Development', 'Mobile Development', 'Cloud Computing', 'AI/ML', 'DevOps'].map((interest) => (
                    <label key={interest} className="inline-flex items-center mr-4">
                      <input
                        type="checkbox"
                        checked={formData.interests.includes(interest)}
                        onChange={(e) => {
                          const newInterests = e.target.checked
                            ? [...formData.interests, interest]
                            : formData.interests.filter(i => i !== interest);
                          setFormData({ ...formData, interests: newInterests });
                        }}
                        className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                      />
                      <span className="ml-2 text-sm text-gray-700">{interest}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-6">
              <div>
                <div className="flex items-center mb-4">
                  <Award className="h-5 w-5 text-indigo-500 mr-2" />
                  <label className="block text-sm font-medium text-gray-700">
                    Technical Skills
                  </label>
                </div>
                 
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  {Object.entries(skillCategories).map(([category, skills]) => (
                    <div key={category} className="space-y-4">
                      <h4 className="text-sm font-medium text-gray-900 capitalize">{category}</h4>
                      <div className="space-y-2">
                        {skills.map((skill) => (
                          <label key={skill} className="flex items-center">
                            <input
                              type="checkbox"
                              checked={formData.skills[category as keyof typeof formData.skills].includes(skill)}
                              onChange={(e) => {
                                const newSkills = e.target.checked
                                  ? [...formData.skills[category as keyof typeof formData.skills], skill]
                                  : formData.skills[category as keyof typeof formData.skills].filter(s => s !== skill);
                                setFormData({
                                  ...formData,
                                  skills: {
                                    ...formData.skills,
                                    [category]: newSkills
                                  }
                                });
                              }}
                              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                            />
                            <span className="ml-2 text-sm text-gray-700">{skill}</span>
                          </label>
                         ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="px-6 py-4 bg-gray-50 flex justify-between">
          {step > 1 && (
            <button
              onClick={() => setStep(step - 1)}
              className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              Back
            </button>
          )}
          {step < 3 ? (
            <button
              onClick={() => setStep(step + 1)}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Next
              <ChevronRight className="ml-2 h-4 w-4" />
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                  Analyzing...
                </>
              ) : (
                <>
              <Target className="ml-2 h-4 w-4" />
                  Get Recommendations
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}