'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Organization, OrganizationMember, OrganizationRole, InviteUserRequest } from '@/types/organization';
import { organizationApi } from '@/api/organizations';

export default function OrganizationDetailPage() {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [userRole, setUserRole] = useState<OrganizationRole | null>(null);
  const [loading, setLoading] = useState(true);
  const [membersLoading, setMembersLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteFormData, setInviteFormData] = useState<InviteUserRequest>({
    email: '',
    role: OrganizationRole.MEMBER,
  });
  
  const router = useRouter();
  const params = useParams();
  const orgId = params.id as string;

  useEffect(() => {
    if (orgId) {
      loadOrganizationData();
    }
  }, [orgId]);

  const loadOrganizationData = async () => {
    try {
      setLoading(true);
      
      // Get user's organizations to find this one
      const organizations = await organizationApi.getUserOrganizations();
      const currentOrg = organizations.find(org => org.id === orgId);
      
      if (!currentOrg) {
        setError('Organization not found or access denied');
        return;
      }
      
      setOrganization(currentOrg);
      
      // Get user's role in this organization
      const roleResponse = await organizationApi.getUserRole(orgId);
      setUserRole(roleResponse.role);
      
      // Load members if user is admin
      if (roleResponse.role === OrganizationRole.ADMIN) {
        loadMembers();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load organization');
    } finally {
      setLoading(false);
    }
  };

  const loadMembers = async () => {
    try {
      setMembersLoading(true);
      const orgMembers = await organizationApi.getOrganizationMembers(orgId);
      setMembers(orgMembers);
    } catch (err) {
      console.error('Failed to load members:', err);
    } finally {
      setMembersLoading(false);
    }
  };

  const handleInviteUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await organizationApi.inviteUser(orgId, inviteFormData);
      setShowInviteForm(false);
      setInviteFormData({ email: '', role: OrganizationRole.MEMBER });
      loadMembers(); // Refresh members list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to invite user');
    }
  };

  const handleRemoveUser = async (userId: string) => {
    if (!confirm('Are you sure you want to remove this user from the organization?')) {
      return;
    }
    
    try {
      await organizationApi.removeUser(orgId, userId);
      loadMembers(); // Refresh members list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove user');
    }
  };

  const handleUpdateRole = async (userId: string, newRole: OrganizationRole) => {
    try {
      await organizationApi.updateUserRole(orgId, userId, newRole);
      loadMembers(); // Refresh members list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user role');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-base-200 flex items-center justify-center">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  if (error || !organization) {
    return (
      <div className="min-h-screen bg-base-200 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-error mb-4">Error</h1>
          <p className="text-base-content/70 mb-4">{error || 'Organization not found'}</p>
          <button className="btn btn-primary" onClick={() => router.push('/organizations')}>
            Back to Organizations
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-4">
      <div className="max-w-6xl mx-auto">
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
            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <h2 className="card-title">Organization Details</h2>
                <div className="space-y-2">
                  <div>
                    <span className="font-semibold">Members:</span> {organization.member_count}
                  </div>
                  <div>
                    <span className="font-semibold">Your Role:</span>{' '}
                    <span className={`badge ${userRole === OrganizationRole.ADMIN ? 'badge-primary' : 'badge-outline'}`}>
                      {userRole}
                    </span>
                  </div>
                  <div>
                    <span className="font-semibold">Created:</span> {new Date(organization.created_at).toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Members Section */}
          <div className="lg:col-span-2">
            <div className="card bg-base-100 shadow-xl">
              <div className="card-body">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="card-title">Members</h2>
                  {userRole === OrganizationRole.ADMIN && (
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => setShowInviteForm(true)}
                    >
                      Invite Member
                    </button>
                  )}
                </div>

                {userRole === OrganizationRole.ADMIN ? (
                  <>
                    {membersLoading ? (
                      <div className="flex justify-center py-8">
                        <div className="loading loading-spinner loading-lg"></div>
                      </div>
                    ) : (
                      <div className="overflow-x-auto">
                        <table className="table table-zebra">
                          <thead>
                            <tr>
                              <th>Name</th>
                              <th>Email</th>
                              <th>Role</th>
                              <th>Joined</th>
                              <th>Actions</th>
                            </tr>
                          </thead>
                          <tbody>
                            {members.map((member) => (
                              <tr key={member.user_id}>
                                <td>{member.full_name || 'N/A'}</td>
                                <td>{member.email}</td>
                                <td>
                                  <select 
                                    className="select select-bordered select-sm"
                                    value={member.role}
                                    onChange={(e) => handleUpdateRole(member.user_id, e.target.value as OrganizationRole)}
                                    disabled={member.user_id === organization.owner_id}
                                  >
                                    <option value={OrganizationRole.MEMBER}>Member</option>
                                    <option value={OrganizationRole.ADMIN}>Admin</option>
                                  </select>
                                </td>
                                <td>{new Date(member.joined_at).toLocaleDateString()}</td>
                                <td>
                                  {member.user_id !== organization.owner_id && (
                                    <button 
                                      className="btn btn-error btn-sm"
                                      onClick={() => handleRemoveUser(member.user_id)}
                                    >
                                      Remove
                                    </button>
                                  )}
                                </td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="text-center py-8 text-base-content/60">
                    <p>Member list is only visible to organization administrators.</p>
                    <p className="text-sm mt-2">You can see general organization information above.</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Invite Form Modal */}
        {showInviteForm && (
          <div className="modal modal-open">
            <div className="modal-box">
              <h3 className="font-bold text-lg mb-4">Invite New Member</h3>
              <form onSubmit={handleInviteUser} className="space-y-4">
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Email Address</span>
                  </label>
                  <input
                    type="email"
                    className="input input-bordered"
                    value={inviteFormData.email}
                    onChange={(e) => setInviteFormData({ ...inviteFormData, email: e.target.value })}
                    required
                  />
                </div>
                <div className="form-control">
                  <label className="label">
                    <span className="label-text">Role</span>
                  </label>
                  <select
                    className="select select-bordered"
                    value={inviteFormData.role}
                    onChange={(e) => setInviteFormData({ ...inviteFormData, role: e.target.value as OrganizationRole })}
                  >
                    <option value={OrganizationRole.MEMBER}>Member</option>
                    <option value={OrganizationRole.ADMIN}>Admin</option>
                  </select>
                </div>
                <div className="modal-action">
                  <button type="submit" className="btn btn-primary">
                    Send Invitation
                  </button>
                  <button 
                    type="button" 
                    className="btn btn-outline"
                    onClick={() => setShowInviteForm(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}