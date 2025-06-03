'use client';

import { useState, useEffect, useCallback, memo } from 'react';
import { 
  OrganizationMember, 
  OrganizationRole, 
  InviteUserRequest,
  getRolePermissions,
  canManageUser,
  getRoleDisplayName,
  getRoleDescription
} from '@/types/organization';
import { organizationApi } from '@/api/organizations';

interface MemberManagementProps {
  organizationId: string;
  ownerId: string;
  userRole: OrganizationRole;
}

function MemberManagement({ organizationId, ownerId, userRole }: MemberManagementProps) {
  const [members, setMembers] = useState<OrganizationMember[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteFormData, setInviteFormData] = useState<InviteUserRequest>({
    email: '',
    role: OrganizationRole.MEMBER,
  });
  const [inviteLoading, setInviteLoading] = useState(false);
  const [transferOwnershipUserId, setTransferOwnershipUserId] = useState<string | null>(null);

  const permissions = getRolePermissions(userRole);

  const loadMembers = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const orgMembers = await organizationApi.getOrganizationMembers(organizationId);
      setMembers(orgMembers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load members');
    } finally {
      setLoading(false);
    }
  }, [organizationId]);

  useEffect(() => {
    if (permissions.canManageMembers) {
      loadMembers();
    }
  }, [loadMembers, permissions.canManageMembers]);

  const handleInviteUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviteLoading(true);
    setError(null);

    try {
      await organizationApi.inviteUser(organizationId, inviteFormData);
      setShowInviteForm(false);
      setInviteFormData({ email: '', role: OrganizationRole.MEMBER });
      loadMembers(); // Refresh members list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to invite user');
    } finally {
      setInviteLoading(false);
    }
  };

  const handleRemoveUser = async (userId: string) => {
    if (!confirm('Are you sure you want to remove this user from the organization?')) {
      return;
    }
    
    try {
      setError(null);
      await organizationApi.removeUser(organizationId, userId);
      loadMembers(); // Refresh members list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to remove user');
    }
  };

  const handleUpdateRole = async (userId: string, newRole: OrganizationRole) => {
    try {
      setError(null);
      await organizationApi.updateUserRole(organizationId, userId, newRole);
      loadMembers(); // Refresh members list
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update user role');
    }
  };

  const handleTransferOwnership = async () => {
    if (!transferOwnershipUserId) return;
    
    if (!confirm('Are you sure you want to transfer ownership? This action cannot be undone. You will become an Admin after the transfer.')) {
      return;
    }
    
    try {
      setError(null);
      await organizationApi.transferOwnership(organizationId, transferOwnershipUserId);
      setTransferOwnershipUserId(null);
      loadMembers(); // Refresh members list
      // Note: In a real app, we should redirect or refresh the page since user's role has changed
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to transfer ownership');
    }
  };

  if (!permissions.canManageMembers) {
    return (
      <div className="text-center py-8 text-base-content/60">
        <p>Member management is only available to users with management privileges.</p>
        <p className="text-sm mt-2">Your role: {getRoleDisplayName(userRole)}</p>
        <p className="text-xs mt-1 text-base-content/40">{getRoleDescription(userRole)}</p>
      </div>
    );
  }

  return (
    <>
      <div className="flex justify-between items-center mb-4">
        <h2 className="card-title">Members</h2>
        <button 
          className="btn btn-primary btn-sm"
          onClick={() => setShowInviteForm(true)}
        >
          Invite Member
        </button>
      </div>

      {error && (
        <div className="alert alert-error mb-4">
          <span>{error}</span>
        </div>
      )}

      {loading ? (
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
                    {canManageUser(userRole, member.role) && member.user_id !== ownerId ? (
                      <select 
                        className="select select-bordered select-sm"
                        value={member.role}
                        onChange={(e) => handleUpdateRole(member.user_id, e.target.value as OrganizationRole)}
                      >
                        <option value={OrganizationRole.VIEWER}>Viewer</option>
                        <option value={OrganizationRole.MEMBER}>Member</option>
                        <option value={OrganizationRole.MANAGER}>Manager</option>
                        {permissions.canManageAdmins && (
                          <option value={OrganizationRole.ADMIN}>Admin</option>
                        )}
                      </select>
                    ) : (
                      <span className={`badge ${
                        member.role === OrganizationRole.OWNER ? 'badge-primary' :
                        member.role === OrganizationRole.ADMIN ? 'badge-secondary' :
                        member.role === OrganizationRole.MANAGER ? 'badge-accent' :
                        member.role === OrganizationRole.MEMBER ? 'badge-neutral' :
                        'badge-ghost'
                      }`}>
                        {getRoleDisplayName(member.role)}
                      </span>
                    )}
                  </td>
                  <td>{new Date(member.joined_at).toLocaleDateString()}</td>
                  <td>
                    <div className="flex gap-2">
                      {canManageUser(userRole, member.role) && member.user_id !== ownerId && (
                        <button 
                          className="btn btn-error btn-sm"
                          onClick={() => handleRemoveUser(member.user_id)}
                        >
                          Remove
                        </button>
                      )}
                      {permissions.canTransferOwnership && member.user_id !== ownerId && (
                        <button 
                          className="btn btn-warning btn-sm"
                          onClick={() => setTransferOwnershipUserId(member.user_id)}
                        >
                          Transfer Ownership
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Invite Form Modal */}
      {showInviteForm && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4">Invite New Member</h3>
            
            {error && (
              <div className="alert alert-error mb-4">
                <span>{error}</span>
              </div>
            )}

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
                  disabled={inviteLoading}
                  placeholder="user@example.com"
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
                  disabled={inviteLoading}
                >
                  <option value={OrganizationRole.VIEWER}>Viewer</option>
                  <option value={OrganizationRole.MEMBER}>Member</option>
                  <option value={OrganizationRole.MANAGER}>Manager</option>
                  {permissions.canManageAdmins && (
                    <option value={OrganizationRole.ADMIN}>Admin</option>
                  )}
                </select>
                <label className="label">
                  <span className="label-text-alt text-xs">
                    {getRoleDescription(inviteFormData.role)}
                  </span>
                </label>
              </div>

              <div className="modal-action">
                <button 
                  type="submit" 
                  className={`btn btn-primary ${inviteLoading ? 'loading' : ''}`}
                  disabled={inviteLoading}
                >
                  {inviteLoading ? 'Sending...' : 'Send Invitation'}
                </button>
                <button 
                  type="button" 
                  className="btn btn-outline"
                  onClick={() => setShowInviteForm(false)}
                  disabled={inviteLoading}
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Transfer Ownership Confirmation Modal */}
      {transferOwnershipUserId && (
        <div className="modal modal-open">
          <div className="modal-box">
            <h3 className="font-bold text-lg mb-4 text-warning">Transfer Organization Ownership</h3>
            
            {error && (
              <div className="alert alert-error mb-4">
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-4">
              <div className="alert alert-warning">
                <div>
                  <h4 className="font-semibold">Warning: This action cannot be undone!</h4>
                  <p className="text-sm mt-1">
                    You are about to transfer ownership of this organization to{' '}
                    <strong>
                      {members.find(m => m.user_id === transferOwnershipUserId)?.email}
                    </strong>
                  </p>
                  <p className="text-sm mt-2">After the transfer:</p>
                  <ul className="text-sm list-disc list-inside mt-1 space-y-1">
                    <li>You will become an Admin (losing owner privileges)</li>
                    <li>The new owner will have full control over the organization</li>
                    <li>Only the new owner can delete the organization</li>
                    <li>Only the new owner can transfer ownership again</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="modal-action">
              <button 
                className="btn btn-warning"
                onClick={handleTransferOwnership}
              >
                Confirm Transfer
              </button>
              <button 
                className="btn btn-outline"
                onClick={() => setTransferOwnershipUserId(null)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default memo(MemberManagement);