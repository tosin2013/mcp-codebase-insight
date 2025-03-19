import React, { useState } from 'react';
import { X, Send, HelpCircle } from 'lucide-react';

interface HelpRequestProps {
  onClose: () => void;
}

export function HelpRequest({ onClose }: HelpRequestProps) {
  const [formData, setFormData] = useState({
    category: '',
    title: '',
    description: '',
    skillsNeeded: '',
    timeframe: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full mx-4 overflow-hidden">
        <div className="px-6 py-4 bg-green-600 text-white flex justify-between items-center">
          <h3 className="text-lg font-medium flex items-center">
            <HelpCircle className="h-5 w-5 mr-2" />
            Request Help
          </h3>
          <button onClick={onClose} className="text-white hover:text-gray-200">
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="px-6 py-4">
          <div className="space-y-4">
            <div>
              <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                Help Category
              </label>
              <select
                id="category"
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
              >
                <option value="">Select a category</option>
                <option value="portfolio-review">Portfolio Review</option>
                <option value="project-help">Project Help</option>
                <option value="skill-development">Skill Development</option>
                <option value="career-advice">Career Advice</option>
              </select>
            </div>

            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Title
              </label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="E.g., Need help with React project structure"
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                id="description"
                rows={4}
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="Describe what kind of help you need..."
              />
            </div>

            <div>
              <label htmlFor="skillsNeeded" className="block text-sm font-medium text-gray-700">
                Skills Needed
              </label>
              <input
                type="text"
                id="skillsNeeded"
                value={formData.skillsNeeded}
                onChange={(e) => setFormData({ ...formData, skillsNeeded: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="E.g., React, TypeScript, AWS"
              />
            </div>

            <div>
              <label htmlFor="timeframe" className="block text-sm font-medium text-gray-700">
                Timeframe
              </label>
              <input
                type="text"
                id="timeframe"
                value={formData.timeframe}
                onChange={(e) => setFormData({ ...formData, timeframe: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500"
                placeholder="E.g., Next 2 weeks"
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700"
            >
              <Send className="h-4 w-4 mr-2" />
              Submit Request
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}