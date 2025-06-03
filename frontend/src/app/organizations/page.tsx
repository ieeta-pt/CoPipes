'use client';

import OrganizationList from '@/components/organization/OrganizationList';

export default function OrganizationsPage() {
  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-6xl mx-auto">
        <OrganizationList />
      </div>
    </div>
  );
}