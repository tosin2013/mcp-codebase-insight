import React from 'react';
import { ExternalLink as ExternalLinkIcon } from 'lucide-react';
import type { ExternalLink } from '../../types';

interface ExternalLinkDisplayProps {
  link: ExternalLink;
  variant?: 'inline' | 'card';
}

export function ExternalLinkDisplay({ link, variant = 'inline' }: ExternalLinkDisplayProps) {
  if (variant === 'card') {
    return (
      <div className="bg-white rounded-lg shadow-sm p-4 hover:shadow-md transition-shadow">
        <a
          href={link.url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={() => {
            // In a real app, this would call an API to increment the click count
            console.log('Link clicked:', link.id);
          }}
          className="block"
        >
          <h3 className="text-lg font-medium text-gray-900 group-hover:text-indigo-600">
            {link.title}
            {link.isAffiliate && (
              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                Affiliate
              </span>
            )}
          </h3>
          {link.description && (
            <p className="mt-1 text-sm text-gray-500">{link.description}</p>
          )}
          <div className="mt-2 flex items-center text-sm text-gray-500">
            <ExternalLinkIcon className="mr-1.5 h-4 w-4 flex-shrink-0" />
            <span>Visit Resource</span>
          </div>
        </a>
      </div>
    );
  }

  return (
    <a
      href={link.url}
      target="_blank"
      rel="noopener noreferrer"
      onClick={() => {
        // In a real app, this would call an API to increment the click count
        console.log('Link clicked:', link.id);
      }}
      className="inline-flex items-center text-indigo-600 hover:text-indigo-900"
    >
      {link.title}
      {link.isAffiliate && (
        <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
          Affiliate
        </span>
      )}
      <ExternalLinkIcon className="ml-1.5 h-4 w-4" />
    </a>
  );
}