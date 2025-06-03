'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Organization, OrganizationCreateRequest, OrganizationRole } from '@/types/organization';
import { organizationApi } from '@/api/organizations';

export default function OrganizationsPage() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createFormData, setCreateFormData] = useState<OrganizationCreateRequest>({
    name: '',
    description: '',
  });
  const router = useRouter();

  useEffect(() => {
    loadOrganizations();
  }, []);

  const loadOrganizations = async () => {
    try {
      const orgs = await organizationApi.getUserOrganizations();
      setOrganizations(orgs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load organizations');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrganization = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await organizationApi.createOrganization(createFormData);
      setShowCreateForm(false);
      setCreateFormData({ name: '', description: '' });
      loadOrganizations();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create organization');
    }
  };

  const handleOrganizationClick = (orgId: string) => {
    router.push(`/organizations/${orgId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-200 flex items-center justify-center">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">Organizations</h1>
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateForm(true)}
          >
            Create Organization
          </button>
        </div>

        {error && (
          <div className="alert alert-error mb-4">
            <span>{error}</span>
          </div>
        )}

        {showCreateForm && (
          <div className="card bg-base-100 shadow-xl mb-6">
            <div className="card-body">
              <h2 className="card-title">Create New Organization</h2>
              <form onSubmit={handleCreateOrganization} className="space-y-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Organization Name</span>
                  </label>
                  <input
                    type="text"
                    className="input input-bordered"
                    value={createFormData.name}
                    onChange={(e) => setCreateFormData({ ...createFormData, name: e.target.value })}
                    required
                  />
                </div>
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Description (optional)</span>
                  </label>
                  <textarea
                    className="textarea textarea-bordered"
                    value={createFormData.description}
                    onChange={(e) => setCreateFormData({ ...createFormData, description: e.target.value })}
                  />
                </div>
                <div className="flex gap-2">
                  <button type="submit" className="btn btn-primary">
                    Create
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-outline"
                    onClick={() => setShowCreateForm(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {organizations.map((org) => (
            <div 
              key={org.id} 
              className="card bg-base-100 shadow-xl cursor-pointer hover:shadow-2xl transition-shadow"
              onClick={() => handleOrganizationClick(org.id)}
            >
              <div className="card-body">
                <h2 className="card-title">{org.name}</h2>
                {org.description && (
                  <p className="text-base-content/70">{org.description}</p>
                )}
                <div className="flex justify-between items-center mt-4">
                  <div className="badge badge-outline">
                    {org.member_count} member{org.member_count !== 1 ? 's' : ''}
                  </div>
                  <div className="text-sm text-base-content/70">
                    Created {new Date(org.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {organizations.length === 0 && (
          <div className="text-center py-12">
            <h2 className="text-xl font-semibold mb-2">No Organizations Yet</h2>
            <p className="text-base-content/70 mb-4">
              Create your first organization to start collaborating with your team.
            </p>
            <button 
              className="btn btn-primary"
              onClick={() => setShowCreateForm(true)}
            >
              Create Organization
            </button>
          </div>
        )}
      </div>
    </div>
  );
}