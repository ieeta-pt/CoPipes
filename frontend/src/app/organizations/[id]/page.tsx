'use client';

import { useParams } from 'next/navigation';
import OrganizationDetails from '@/components/organization/OrganizationDetails';

export default function OrganizationDetailPage() {
  const params = useParams();
  const orgId = params?.id as string;

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-6xl mx-auto">
        <OrganizationDetails organizationId={orgId} />
      </div>
    </div>
  );
}