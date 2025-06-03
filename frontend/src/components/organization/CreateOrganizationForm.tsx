'use client';

import { useState } from 'react';
import { OrganizationCreateRequest } from '@/types/organization';
import { organizationApi } from '@/api/organizations';

interface CreateOrganizationFormProps {
  onSuccess: () => void;
  onCancel: () => void;
}

export default function CreateOrganizationForm({ onSuccess, onCancel }: CreateOrganizationFormProps) {
  const [formData, setFormData] = useState<OrganizationCreateRequest>({
    name: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await organizationApi.createOrganization(formData);
      onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create organization');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">Create New Organization</h2>
        
        {error && (
          <div className="alert alert-error mb-4">
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="form-control">
            <label className="label">
              <span className="label-text">Organization Name</span>
            </label>
            <input
              type="text"
              className="input input-bordered"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              disabled={loading}
              placeholder="Enter organization name"
            />
          </div>

          <div className="form-control">
            <label className="label">
              <span className="label-text">Description (optional)</span>
            </label>
            <textarea
              className="textarea textarea-bordered"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              disabled={loading}
              placeholder="Describe your organization"
              rows={3}
            />
          </div>

          <div className="flex gap-2 pt-4">
            <button 
              type="submit" 
              className={`btn btn-primary ${loading ? 'loading' : ''}`}
              disabled={loading || !formData.name.trim()}
            >
              {loading ? 'Creating...' : 'Create Organization'}
            </button>
            <button 
              type="button" 
              className="btn btn-outline"
              onClick={onCancel}
              disabled={loading}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}