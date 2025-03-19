import React from 'react';
import PropTypes from 'prop-types';
import { Star, Shield, Award } from 'lucide-react';
import type { Skill } from '../../types';

interface SkillCardProps {
  skill: Skill;
  onEndorse?: (skillName: string) => void;
  onViewDetails?: (skillName: string) => void;
}

export function SkillCard({ skill, onEndorse, onViewDetails }: SkillCardProps) {
  const getLevelColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-orange-100 text-orange-800';
      case 'expert':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-medium text-gray-900">{skill.name}</h3>
          <span className={`mt-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getLevelColor(skill.level)}`}>
            {skill.level.charAt(0).toUpperCase() + skill.level.slice(1)}
          </span>
        </div>
        {skill.verified && (
          <Shield className="h-5 w-5 text-indigo-600" />
        )}
      </div>

      <div className="mt-4 flex items-center space-x-2">
        <Award className="h-4 w-4 text-yellow-400" />
        <span className="text-sm text-gray-500">
          {skill.endorsements} endorsements
        </span>
      </div>

      <div className="mt-4 flex justify-between items-center">
        <button 
          onClick={() => onEndorse?.(skill.name)}
          className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
        >
          <Star className="h-4 w-4 mr-1" />
          Endorse
        </button>
        <button 
          onClick={() => onViewDetails?.(skill.name)}
          className="text-sm text-gray-500 hover:text-indigo-600"
        >
          View Details
        </button>
      </div>
    </div>
  );
}

// PropTypes validation
SkillCard.propTypes = {
  skill: PropTypes.shape({
    name: PropTypes.string.isRequired,
    level: PropTypes.oneOf(['beginner', 'intermediate', 'advanced', 'expert']).isRequired,
    endorsements: PropTypes.number.isRequired,
    verified: PropTypes.bool.isRequired
  }).isRequired,
  onEndorse: PropTypes.func,
  onViewDetails: PropTypes.func
};