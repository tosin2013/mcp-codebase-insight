import React, { useState, useEffect } from 'react';
import { supabase } from '../../lib/supabase';
import { ExternalLinkForm } from './ExternalLinkForm';
import { ExternalLinkEditForm } from './ExternalLinkEditForm';
import { Loader2, Edit, Trash2, ExternalLink as ExternalLinkIcon } from 'lucide-react';
import type { ExternalLink } from '../../types';

export function ManageLinks() {
  const [links, setLinks] = useState<ExternalLink[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingLink, setEditingLink] = useState<ExternalLink | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    url: '',
    category: '',
    description: '',
    priority: 0,
    active: true
  });

  useEffect(() => {
    fetchLinks();
  }, []);

  async function fetchLinks() {
    try {
      setLoading(true);
      setError(null);
      
      const { data, error: fetchError } = await supabase
        .from('external_links')
        .select('*')
        .order('priority', { ascending: false });

      if (fetchError) throw fetchError;

      // Transform the data to match our ExternalLink type
      const formattedLinks = data.map(link => ({
        id: link.id,
        title: link.title,
        url: link.url,
        category: link.category,
        description: link.description || '',
        priority: link.priority,
        active: link.active,
        createdAt: new Date(link.created_at),
        updatedAt: new Date(link.updated_at)
      }));

      setLinks(formattedLinks);
    } catch (err) {
      console.error('Error fetching links:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch links');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const { data, error: submitError } = await supabase
        .from('external_links')
        .insert([
          {
            title: formData.title,
            url: formData.url,
            category: formData.category,
            description: formData.description,
            priority: formData.priority,
            active: formData.active
          }
        ])
        .select()
        .single();

      if (submitError) throw submitError;

      // Add the new link to the list
      setLinks([data, ...links]);
      
      // Reset form
      setFormData({
        title: '',
        url: '',
        category: '',
        description: '',
        priority: 0,
        active: true
      });
    } catch (err) {
      console.error('Error adding link:', err);
      setError(err instanceof Error ? err.message : 'Failed to add link');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: string) {
    if (!window.confirm('Are you sure you want to delete this link?')) return;

    try {
      const { error: deleteError } = await supabase
        .from('external_links')
        .delete()
        .eq('id', id);

      if (deleteError) throw deleteError;

      setLinks(links.filter(link => link.id !== id));
    } catch (err) {
      console.error('Error deleting link:', err);
      setError(err instanceof Error ? err.message : 'Failed to delete link');
    }
  }

  function handleEdit(link: ExternalLink) {
    setEditingLink(link);
  }

  function handleUpdate(updatedLink: ExternalLink) {
    setLinks(links.map(link => 
      link.id === updatedLink.id ? updatedLink : link
    ));
    setEditingLink(null);
  }

  return (
    <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div className="px-4 py-6 sm:px-0">
        <div className="border-b border-gray-200 pb-5">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
            Manage External Links
          </h2>
          <p className="mt-2 max-w-4xl text-sm text-gray-500">
            Add and manage external links that will be displayed across the platform.
          </p>
        </div>

        {error && (
          <div className="mt-4 bg-red-50 border-l-4 border-red-400 p-4">
            <div className="flex">
              <div className="flex-shrink-0">⚠</div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-6 space-y-6 bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
            <div className="sm:col-span-4">
              <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                Title
              </label>
              <div className="mt-1">
                <input
                  type="text"
                  name="title"
                  id="title"
                  required
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>

            <div className="sm:col-span-4">
              <label htmlFor="url" className="block text-sm font-medium text-gray-700">
                URL
              </label>
              <div className="mt-1">
                <input
                  type="url"
                  name="url"
                  id="url"
                  required
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>

            <div className="sm:col-span-3">
              <label htmlFor="category" className="block text-sm font-medium text-gray-700">
                Category
              </label>
              <div className="mt-1">
                <select
                  id="category"
                  name="category"
                  required
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                >
                  <option value="">Select a category</option>
                  <option value="Learning Path">Learning Path</option>
                  <option value="Project Resources">Project Resources</option>
                  <option value="Networking Tools">Networking Tools</option>
                  <option value="Portfolio Resources">Portfolio Resources</option>
                </select>
              </div>
            </div>

            <div className="sm:col-span-6">
              <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                Description
              </label>
              <div className="mt-1">
                <textarea
                  id="description"
                  name="description"
                  rows={3}
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>

            <div className="sm:col-span-2">
              <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                Priority
              </label>
              <div className="mt-1">
                <input
                  type="number"
                  name="priority"
                  id="priority"
                  min="0"
                  max="100"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) })}
                  className="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md"
                />
              </div>
            </div>

            <div className="sm:col-span-2">
              <div className="flex items-center h-full">
                <input
                  type="checkbox"
                  id="active"
                  name="active"
                  checked={formData.active}
                  onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                />
                <label htmlFor="active" className="ml-2 block text-sm text-gray-700">
                  Active
                </label>
              </div>
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Loader2 className="animate-spin -ml-1 mr-2 h-4 w-4" />
                  Adding...
                </>
              ) : (
                'Add Link'
              )}
            </button>
          </div>
        </form>

        <div className="mt-8">
          <div className="flex flex-col">
            <div className="-my-2 overflow-x-auto sm:-mx-6 lg:-mx-8">
              <div className="py-2 align-middle inline-block min-w-full sm:px-6 lg:px-8">
                <div className="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Title
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Category
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Priority
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th scope="col" className="relative px-6 py-3">
                          <span className="sr-only">Actions</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {links.map((link) => (
                        <tr key={link.id}>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm font-medium text-gray-900">{link.title}</div>
                            <div className="text-sm text-gray-500">
                              <a href={link.url} target="_blank" rel="noopener noreferrer" className="hover:text-indigo-600">
                                {link.url}
                              </a>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{link.category}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{link.priority}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              link.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                            }`}>
                              {link.active ? 'Active' : 'Inactive'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex justify-end space-x-2">
                              <button
                                onClick={() => handleEdit(link)}
                                className="text-indigo-600 hover:text-indigo-900"
                              >
                                <Edit className="h-5 w-5" />
                                <span className="sr-only">Edit</span>
                              </button>
                              <button
                                onClick={() => handleDelete(link.id)}
                                className="text-red-600 hover:text-red-900"
                              >
                                <Trash2 className="h-5 w-5" />
                                <span className="sr-only">Delete</span>
                              </button>
                              <a
                                href={link.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-gray-400 hover:text-gray-600"
                              >
                                <ExternalLinkIcon className="h-5 w-5" />
                                <span className="sr-only">Visit</span>
                              </a>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {editingLink && (
        <ExternalLinkEditForm
          link={editingLink}
          onClose={() => setEditingLink(null)}
          onUpdate={handleUpdate}
        />
      )}
    </div>
  );
}