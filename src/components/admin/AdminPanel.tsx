import React, { useState } from 'react';
import { ExternalLinkForm } from './ExternalLinkForm';
import { ExternalLinkTable } from './ExternalLinkTable';
import type { ExternalLink } from '../../types';

// In a real app, this would be fetched from an API
const mockLinks: ExternalLink[] = [
  {
    id: '1',
    title: 'Learn React',
    url: 'https://react.dev',
    category: 'Learning Path',
    isAffiliate: false,
    description: 'Official React documentation',
    clicks: 150,
    createdAt: new Date('2024-01-01'),
    updatedAt: new Date('2024-01-01'),
  },
  {
    id: '2',
    title: 'AWS Cloud Practitioner Course',
    url: 'https://aws.amazon.com/training',
    category: 'Learning Path',
    isAffiliate: true,
    description: 'Get certified as an AWS Cloud Practitioner',
    clicks: 75,
    createdAt: new Date('2024-01-02'),
    updatedAt: new Date('2024-01-02'),
  },
];

export function AdminPanel() {
  const [links, setLinks] = useState<ExternalLink[]>(mockLinks);
  const [editingLink, setEditingLink] = useState<ExternalLink | null>(null);

  const handleSubmit = (linkData: Omit<ExternalLink, 'id' | 'clicks' | 'createdAt' | 'updatedAt'>) => {
    if (editingLink) {
      // Update existing link
      setLinks(links.map(link =>
        link.id === editingLink.id
          ? {
              ...link,
              ...linkData,
              updatedAt: new Date(),
            }
          : link
      ));
      setEditingLink(null);
    } else {
      // Add new link
      const newLink: ExternalLink = {
        ...linkData,
        id: Math.random().toString(36).substr(2, 9),
        clicks: 0,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      setLinks([...links, newLink]);
    }
  };

  const handleEdit = (link: ExternalLink) => {
    setEditingLink(link);
  };

  const handleDelete = (id: string) => {
    setLinks(links.filter(link => link.id !== id));
  };

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="border-b border-gray-200 pb-5">
          <h3 className="text-2xl font-semibold leading-6 text-gray-900">External Links Management</h3>
          <p className="mt-2 max-w-4xl text-sm text-gray-500">
            Add and manage external links, including affiliate links, that will be displayed across the platform.
          </p>
        </div>

        <div className="mt-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <div className="px-4 sm:px-0">
                <h3 className="text-lg font-medium leading-6 text-gray-900">
                  {editingLink ? 'Edit Link' : 'Add New Link'}
                </h3>
                <p className="mt-1 text-sm text-gray-600">
                  {editingLink
                    ? 'Update the details of the existing link.'
                    : 'Add a new external link to the platform.'}
                </p>
              </div>
            </div>
            <div className="mt-5 md:col-span-2 md:mt-0">
              <div className="shadow sm:overflow-hidden sm:rounded-md">
                <div className="space-y-6 bg-white px-4 py-5 sm:p-6">
                  <ExternalLinkForm
                    onSubmit={handleSubmit}
                    initialData={editingLink || undefined}
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-8">
          <h3 className="text-lg font-medium leading-6 text-gray-900">Existing Links</h3>
          <ExternalLinkTable
            links={links}
            onEdit={handleEdit}
            onDelete={handleDelete}
          />
        </div>
      </div>
    </div>
  );
}