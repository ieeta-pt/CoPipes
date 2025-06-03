'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Organization } from '@/types/organization';
import { organizationApi } from '@/api/organizations';
import OrganizationCard from '@/components/organization/OrganizationCard';

export default function ProfileOrganizations() {
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [orgLoading, setOrgLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    loadOrganizations();
  }, []);

  const loadOrganizations = async () => {
    try {
      setOrgLoading(true);
      const userOrgs = await organizationApi.getUserOrganizations();
      setOrganizations(userOrgs);
    } catch (err) {
      console.error("Failed to load organizations:", err);
    } finally {
      setOrgLoading(false);
    }
  };

  const handleCreateOrganization = () => {
    router.push('/organizations');
  };

  const handleOrganizationClick = (orgId: string) => {
    router.push(`/organizations/${orgId}`);
  };

  return (
    <div className="card bg-base-100 shadow-xl mb-6">
      <div className="card-body">
        <div className="flex justify-between items-center mb-4">
          <h2 className="card-title text-2xl font-bold">My Organizations</h2>
          <button 
            className="btn btn-primary"
            onClick={handleCreateOrganization}
          >
            Create Organization
          </button>
        </div>
        
        {orgLoading ? (
          <div className="flex justify-center py-8">
            <div className="loading loading-spinner loading-lg"></div>
          </div>
        ) : organizations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {organizations.map((org) => (
              <OrganizationCard 
                key={org.id}
                organization={org}
                onClick={handleOrganizationClick}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="text-base-content/60 mb-4">
              <svg className="w-16 h-16 mx-auto mb-4 text-base-content/30" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              You're not part of any organizations yet.
            </div>
            <button 
              className="btn btn-primary"
              onClick={handleCreateOrganization}
            >
              Create Your First Organization
            </button>
          </div>
        )}
      </div>
    </div>
  );
}