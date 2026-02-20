'use client';

import { useState, useEffect, useCallback, memo } from 'react';
import { useRouter } from 'next/navigation';
import { Organization } from '@/types/organization';
import { organizationApi } from '@/api/organizations';
import OrganizationCard from './OrganizationCard';
import CreateOrganizationForm from './CreateOrganizationForm';

interface OrganizationListProps {
  onOrganizationCreate?: () => void;
}

function OrganizationList({ onOrganizationCreate }: OrganizationListProps) {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const router = useRouter();

  const loadOrganizations = useCallback(async () => {
    try {
      const orgs = await organizationApi.getUserOrganizations();
      setOrganizations(orgs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load organizations');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOrganizations();
  }, [loadOrganizations]);

  const handleCreateSuccess = useCallback(() => {
    setShowCreateForm(false);
    loadOrganizations();
    onOrganizationCreate?.();
  }, [loadOrganizations, onOrganizationCreate]);

  const handleOrganizationClick = useCallback((orgId: string) => {
    router.push(`/organizations/${orgId}`);
  }, [router]);

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  return (
    <>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Organizations</h1>
        {organizations.length ==! 0 && (
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateForm(true)}
          >
            Create Organization
          </button>
        )}
      </div>

      {error && (
        <div className="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      )}

      {showCreateForm && (
        <div className="mb-6">
          <CreateOrganizationForm 
            onSuccess={handleCreateSuccess}
            onCancel={() => setShowCreateForm(false)}
          />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {organizations.map((org) => (
          <OrganizationCard 
            key={org.id}
            organization={org}
            onClick={handleOrganizationClick}
          />
        ))}
      </div>

      {organizations.length === 0 && (
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold mb-2">No organizations yet</h2>
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
    </>
  );
}

export default memo(OrganizationList);