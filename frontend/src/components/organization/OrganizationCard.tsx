'use client';

import { Organization } from '@/types/organization';

interface OrganizationCardProps {
  organization: Organization;
  onClick: (orgId: string) => void;
}

export default function OrganizationCard({ organization, onClick }: OrganizationCardProps) {
  return (
    <div 
      className="card bg-base-100 shadow-xl cursor-pointer hover:shadow-2xl transition-shadow"
      onClick={() => onClick(organization.id)}
    >
      <div className="card-body">
        <h2 className="card-title">{organization.name}</h2>
        {organization.description && (
          <p className="text-base-content/70">{organization.description}</p>
        )}
        <div className="flex justify-between items-center mt-4">
          <div className="badge badge-outline">
            {organization.member_count} member{organization.member_count !== 1 ? 's' : ''}
          </div>
          <div className="text-sm text-base-content/70">
            Created {new Date(organization.created_at).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  );
}