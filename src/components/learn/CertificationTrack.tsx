import React from 'react';
import { Award, Clock, Book, DollarSign } from 'lucide-react';

interface CertificationTrackProps {
  title: string;
  description: string;
  duration: string;
  level: string;
  examCode: string;
  price: string;
}

export function CertificationTrack({
  title,
  description,
  duration,
  level,
  examCode,
  price
}: CertificationTrackProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden">
      <div className="p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">{title}</h3>
          <Award className="h-6 w-6 text-indigo-600" />
        </div>

        <p className="mt-2 text-sm text-gray-500">{description}</p>

        <div className="mt-4 space-y-2">
          <div className="flex items-center text-sm text-gray-500">
            <Clock className="h-4 w-4 mr-2" />
            Duration: {duration}
          </div>
          <div className="flex items-center text-sm text-gray-500">
            <Book className="h-4 w-4 mr-2" />
            Level: {level}
          </div>
          <div className="flex items-center text-sm text-gray-500">
            <Award className="h-4 w-4 mr-2" />
            Exam Code: {examCode}
          </div>
          <div className="flex items-center text-sm text-gray-500">
            <DollarSign className="h-4 w-4 mr-2" />
            Exam Price: {price}
          </div>
        </div>

        <div className="mt-6">
          <button className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700">
            Start Preparation
          </button>
        </div>
      </div>
    </div>
  );
}