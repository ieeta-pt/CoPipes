'use client';

import { Organization, OrganizationRole, getRoleDisplayName, getRoleDescription } from '@/types/organization';

interface OrganizationInfoCardProps {
  organization: Organization;
  userRole: OrganizationRole;
}

export default function OrganizationInfoCard({ organization, userRole }: OrganizationInfoCardProps) {
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">Organization Details</h2>
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-base-content/70">Members:</span>
            <span className="font-semibold">{organization.member_count}</span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-base-content/70">Your Role:</span>
            <span className={`badge ${
              userRole === OrganizationRole.OWNER ? 'badge-primary' :
              userRole === OrganizationRole.ADMIN ? 'badge-secondary' :
              userRole === OrganizationRole.MANAGER ? 'badge-accent' :
              userRole === OrganizationRole.MEMBER ? 'badge-neutral' :
              'badge-ghost'
            }`}>
              {getRoleDisplayName(userRole)}
            </span>
          </div>
          
          <div className="mt-2">
            <span className="text-xs text-base-content/60">
              {getRoleDescription(userRole)}
            </span>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-sm text-base-content/70">Created:</span>
            <span className="text-sm">{new Date(organization.created_at).toLocaleDateString()}</span>
          </div>
          
          {organization.description && (
            <div className="mt-4">
              <span className="text-sm text-base-content/70">Description:</span>
              <p className="text-sm mt-1">{organization.description}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}