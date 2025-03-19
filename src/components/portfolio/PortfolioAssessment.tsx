import React, { useState, useEffect } from 'react';
import { X, AlertTriangle, CheckCircle, ArrowRight, Clock, History, Bell } from 'lucide-react';
import { supabase } from '../../lib/supabase';

interface AssessmentItem {
  category: string;
  status: 'warning' | 'success';
  message: string;
  suggestion: string;
  completed?: boolean;
  inProgress?: boolean;
  lastUpdated?: string;
}

interface PortfolioAssessmentProps {
  onClose: () => void;
  userId: string;
}

export function PortfolioAssessment({ onClose, userId }: PortfolioAssessmentProps) {
  const [assessmentResults, setAssessmentResults] = useState<AssessmentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [nextAssessment, setNextAssessment] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (userId) {
      loadAssessmentData();
    }
  }, [userId]);

  async function loadAssessmentData() {
    try {
      setLoading(true);
      setError(null);

      // Initialize or get assessment
      const { data: assessment, error: initError } = await supabase
        .rpc('initialize_portfolio_assessment', { user_id: userId });

      if (initError) throw initError;

      if (assessment) {
        setAssessmentResults(assessment.items || []);
        setNextAssessment(assessment.next_assessment ? new Date(assessment.next_assessment) : null);
      }
    } catch (err) {
      console.error('Error loading assessment:', err);
      setError(err instanceof Error ? err.message : 'Failed to load assessment');
    } finally {
      setLoading(false);
    }
  }

  async function updateItemStatus(index: number, status: { completed?: boolean; inProgress?: boolean }) {
    try {
      const updatedResults = [...assessmentResults];
      updatedResults[index] = {
        ...updatedResults[index],
        ...status,
        lastUpdated: new Date().toISOString()
      };

      setAssessmentResults(updatedResults);

      const { error: updateError } = await supabase
        .from('portfolio_assessments')
        .update({
          items: updatedResults,
          updated_at: new Date().toISOString()
        })
        .eq('user_id', userId)
        .single();

      if (updateError) throw updateError;
    } catch (err) {
      console.error('Error updating assessment:', err);
      setError(err instanceof Error ? err.message : 'Failed to update assessment');
    }
  }

  async function scheduleNextAssessment() {
    try {
      const { data: nextDate, error: scheduleError } = await supabase
        .rpc('schedule_next_assessment', { user_id: userId });

      if (scheduleError) throw scheduleError;

      if (nextDate) {
        setNextAssessment(new Date(nextDate));
      }
    } catch (err) {
      console.error('Error scheduling assessment:', err);
      setError(err instanceof Error ? err.message : 'Failed to schedule assessment');
    }
  }

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 overflow-hidden">
        <div className="px-6 py-4 bg-indigo-600 text-white flex justify-between items-center">
          <h3 className="text-lg font-medium">Portfolio Assessment</h3>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="px-6 py-4">
          {error && (
            <div className="mb-4 bg-red-50 border-l-4 border-red-400 p-4">
              <div className="flex">
                <AlertTriangle className="h-5 w-5 text-red-400" />
                <div className="ml-3">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            </div>
          )}

          {loading ? (
            <div className="flex justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : (
            <div className="space-y-4">
              {assessmentResults.map((result, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-start">
                    {result.status === 'warning' ? (
                      <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
                    ) : (
                      <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                    )}
                    <div className="ml-3 flex-1">
                      <h4 className="text-sm font-medium text-gray-900">{result.category}</h4>
                      <p className="mt-1 text-sm text-gray-500">{result.message}</p>
                      <div className="mt-2 flex items-center text-sm text-indigo-600">
                        <ArrowRight className="h-4 w-4 mr-1" />
                        {result.suggestion}
                      </div>
                      {result.lastUpdated && (
                        <p className="mt-1 text-xs text-gray-400">
                          Last updated: {new Date(result.lastUpdated).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <div className="ml-4 flex space-x-2">
                      <button
                        onClick={() => updateItemStatus(index, { inProgress: !result.inProgress })}
                        className={`p-1 rounded ${
                          result.inProgress ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        <Clock className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => updateItemStatus(index, { completed: !result.completed })}
                        className={`p-1 rounded ${
                          result.completed ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        <CheckCircle className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}

              <div className="mt-6 bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <Bell className="h-5 w-5 text-indigo-500 mr-2" />
                    <span className="text-sm text-gray-700">
                      Next assessment: {nextAssessment ? nextAssessment.toLocaleDateString() : 'Not scheduled'}
                    </span>
                  </div>
                  <button
                    onClick={scheduleNextAssessment}
                    className="text-sm text-indigo-600 hover:text-indigo-700"
                  >
                    Schedule Next Review
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="px-6 py-4 bg-gray-50 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Got it, thanks!
          </button>
        </div>
      </div>
    </div>
  );
}