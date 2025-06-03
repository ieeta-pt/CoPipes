'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Organization, OrganizationRole } from '@/types/organization';
import { organizationApi } from '@/api/organizations';
import OrganizationInfoCard from './OrganizationInfoCard';
import MemberManagement from './MemberManagement';

interface OrganizationDetailsProps {
  organizationId: string;
}

export default function OrganizationDetails({ organizationId }: OrganizationDetailsProps) {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [userRole, setUserRole] = useState<OrganizationRole | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const router = useRouter();

  useEffect(() => {
    if (organizationId) {
      loadOrganizationData();
    }
  }, [organizationId]);

  const loadOrganizationData = async () => {
    try {
      setLoading(true);
      
      // Get user's organizations to find this one
      const organizations = await organizationApi.getUserOrganizations();
      const currentOrg = organizations.find(org => org.id === organizationId);
      
      if (!currentOrg) {
        setError('Organization not found or access denied');
        return;
      }
      
      setOrganization(currentOrg);
      
      // Get user's role in this organization
      const roleResponse = await organizationApi.getUserRole(organizationId);
      setUserRole(roleResponse.role);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load organization');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  if (error || !organization) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold text-error mb-4">Error</h1>
        <p className="text-base-content/70 mb-4">{error || 'Organization not found'}</p>
        <button className="btn btn-primary" onClick={() => router.push('/organizations')}>
          Back to Organizations
        </button>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <button 
          className="btn btn-ghost btn-sm"
          onClick={() => router.back()}
        >
          ← Back
        </button>
        <div>
          <h1 className="text-3xl font-bold">{organization.name}</h1>
          {organization.description && (
            <p className="text-base-content/70 mt-1">{organization.description}</p>
          )}
        </div>
      </div>

      {error && (
        <div className="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      )}

      {/* Organization Info */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Organization Details */}
        <div className="lg:col-span-1">
          <OrganizationInfoCard organization={organization} userRole={userRole ?? OrganizationRole.MEMBER} />
        </div>

        {/* Members Section */}
        <div className="lg:col-span-2">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              <MemberManagement 
                organizationId={organizationId}
                ownerId={organization.owner_id}
                userRole={userRole ?? OrganizationRole.VIEWER}
              />
            </div>
          </div>
        </div>
      </div>

    </>
  );
}