'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Organization, OrganizationRole, OrganizationMember } from '@/types/organization';
import { organizationApi } from '@/api/organizations';
import OrganizationInfoCard from './OrganizationInfoCard';
import MemberManagement from './MemberManagement';
import { Trash2, UserCheck } from 'lucide-react';
import { showToast } from '@/components/layout/ShowToast';

interface OrganizationDetailsProps {
  organizationId: string;
}

export default function OrganizationDetails({ organizationId }: OrganizationDetailsProps) {
  const [organization, setOrganization] = useState<Organization | null>(null);
  const [userRole, setUserRole] = useState<OrganizationRole | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [adminMembers, setAdminMembers] = useState<OrganizationMember[]>([]);
  const [selectedNewOwner, setSelectedNewOwner] = useState<string>('');
  const [actionLoading, setActionLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'members' | 'workflows'>('members');
  const [workflows, setWorkflows] = useState<any[]>([]);
  const [workflowsLoading, setWorkflowsLoading] = useState(false);
  
  const router = useRouter();
  const deleteModalRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    if (organizationId) {
      loadOrganizationData();
    }
  }, [organizationId]);

  const loadOrganizationData = async () => {
    try {
      setLoading(true);
      
      // Get user's organizations and role in parallel
      const [organizations, roleResponse] = await Promise.all([
        organizationApi.getUserOrganizations(),
        organizationApi.getUserRole(organizationId)
      ]);
      
      const currentOrg = organizations.find(org => org.id === organizationId);
      
      if (!currentOrg) {
        setError('Organization not found or access denied');
        return;
      }
      
      setOrganization(currentOrg);
      setUserRole(roleResponse.role);

      // If user is owner, load admin members for potential ownership transfer
      if (roleResponse.role === OrganizationRole.OWNER) {
        try {
          const members = await organizationApi.getOrganizationMembers(organizationId);
          const admins = members.filter(member => 
            member.role === OrganizationRole.ADMIN && member.user_id !== currentOrg.owner_id
          );
          setAdminMembers(admins);
        } catch (memberErr) {
          console.error('Failed to load admin members:', memberErr);
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load organization');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteOrganization = async () => {
    if (!organization) return;
    
    try {
      setActionLoading(true);
      await organizationApi.deleteOrganization(organizationId);
      showToast('Organization deleted successfully', 'success');
      router.push('/organizations');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete organization';
      showToast(errorMessage, 'error');
    } finally {
      setActionLoading(false);
      deleteModalRef.current?.close();
    }
  };

  const handleTransferOwnership = async () => {
    if (!organization || !selectedNewOwner) return;
    
    try {
      setActionLoading(true);
      await organizationApi.transferOwnership(organizationId, selectedNewOwner);
      showToast('Ownership transferred successfully', 'success');
      deleteModalRef.current?.close();
      // Reload data to reflect changes
      await loadOrganizationData();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to transfer ownership';
      showToast(errorMessage, 'error');
    } finally {
      setActionLoading(false);
    }
  };

  const openDeleteModal = () => {
    setSelectedNewOwner('');
    deleteModalRef.current?.showModal();
  };

  const loadWorkflows = async () => {
    if (activeTab !== 'workflows') return;
    
    try {
      setWorkflowsLoading(true);
      const result = await organizationApi.getOrganizationWorkflows(organizationId);
      setWorkflows(result.workflows);
    } catch (err) {
      console.error('Failed to load organization workflows:', err);
      showToast('Failed to load workflows', 'error');
    } finally {
      setWorkflowsLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'workflows') {
      loadWorkflows();
    }
  }, [activeTab, organizationId]);

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
      <div className="flex items-center justify-between gap-4 mb-6">
        <div className="flex items-center gap-4">
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
        
        {/* Delete Organization Button - Only for Owners */}
        {userRole === OrganizationRole.OWNER && (
          <button 
            className="btn btn-error btn-sm"
            onClick={openDeleteModal}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Delete Organization
          </button>
        )}
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

        {/* Main Content Section with Tabs */}
        <div className="lg:col-span-2">
          <div className="card bg-base-100 shadow-xl">
            <div className="card-body">
              {/* Tabs */}
              <div className="tabs tabs-boxed mb-6">
                <button 
                  className={`tab ${activeTab === 'members' ? 'tab-active' : ''}`}
                  onClick={() => setActiveTab('members')}
                >
                  Members
                </button>
                <button 
                  className={`tab ${activeTab === 'workflows' ? 'tab-active' : ''}`}
                  onClick={() => setActiveTab('workflows')}
                >
                  Workflows
                </button>
              </div>

              {/* Tab Content */}
              {activeTab === 'members' && (
                <MemberManagement 
                  organizationId={organizationId}
                  ownerId={organization.owner_id}
                  userRole={userRole ?? OrganizationRole.VIEWER}
                />
              )}

              {activeTab === 'workflows' && (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-semibold">Organization Workflows</h3>
                    <button 
                      className="btn btn-primary btn-sm"
                      onClick={() => router.push(`/workflow/editor?org=${organizationId}`)}
                    >
                      Create Workflow
                    </button>
                  </div>

                  {workflowsLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="loading loading-spinner loading-md"></div>
                    </div>
                  ) : workflows.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-base-content/70 mb-4">No workflows created yet for this organization.</p>
                      <button 
                        className="btn btn-primary btn-sm"
                        onClick={() => router.push(`/workflow/editor?org=${organizationId}`)}
                      >
                        Create First Workflow
                      </button>
                    </div>
                  ) : (
                    <div className="overflow-x-auto">
                      <table className="table table-zebra">
                        <thead>
                          <tr>
                            <th>Name</th>
                            <th>Owner</th>
                            <th>Last Edit</th>
                            <th>Status</th>
                            <th>Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {workflows.map((workflow) => (
                            <tr key={workflow.id}>
                              <td className="font-medium">{workflow.name}</td>
                              <td>
                                <div className="flex items-center gap-2">
                                  <div className="w-6 h-6 rounded-full bg-blue-400 flex items-center justify-center text-white text-xs">
                                    {workflow.owner_name?.charAt(0) || workflow.owner_email?.charAt(0) || 'U'}
                                  </div>
                                  <span className="text-sm">
                                    {workflow.owner_name || workflow.owner_email || 'Unknown'}
                                  </span>
                                </div>
                              </td>
                              <td className="text-sm">
                                {workflow.last_edit ? new Date(workflow.last_edit).toLocaleDateString() : 'Never'}
                              </td>
                              <td>
                                <span className={`badge badge-sm ${
                                  workflow.status === 'success' ? 'badge-success' :
                                  workflow.status === 'failed' ? 'badge-error' :
                                  workflow.status === 'running' ? 'badge-warning' :
                                  'badge-info'
                                }`}>
                                  {workflow.status || 'draft'}
                                </span>
                              </td>
                              <td>
                                <div className="flex gap-1">
                                  <button 
                                    className="btn btn-ghost btn-xs"
                                    onClick={() => router.push(`/workflow/editor/${workflow.name.replace(/ /g, '_')}`)}
                                  >
                                    Edit
                                  </button>
                                  <button 
                                    className="btn btn-ghost btn-xs"
                                    onClick={() => router.push(`/workflow/execute/${workflow.name.replace(/ /g, '_')}`)}
                                  >
                                    Run
                                  </button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Delete Organization Modal */}
      <dialog ref={deleteModalRef} className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-lg text-error mb-4">
            <Trash2 className="h-5 w-5 inline mr-2" />
            Delete Organization
          </h3>
          
          <p className="mb-4">
            You are about to delete <strong>{organization.name}</strong>. This action cannot be undone.
          </p>
          
          <p className="mb-6 text-sm text-base-content/70">
            Choose an option below:
          </p>

          {/* Transfer Ownership Option */}
          {adminMembers.length > 0 && (
            <div className="mb-6">
              <label className="label">
                <span className="label-text font-medium">Transfer ownership to an admin:</span>
              </label>
              <select 
                className="select select-bordered w-full"
                value={selectedNewOwner}
                onChange={(e) => setSelectedNewOwner(e.target.value)}
              >
                <option value="">Select new owner...</option>
                {adminMembers.map((admin) => (
                  <option key={admin.user_id} value={admin.user_id}>
                    {admin.user_email} ({admin.user_name || 'No name'})
                  </option>
                ))}
              </select>
            </div>
          )}

          {adminMembers.length === 0 && (
            <div className="alert alert-warning mb-6">
              <span>No admin members available for ownership transfer. You can only delete the organization.</span>
            </div>
          )}

          <div className="modal-action">
            <button 
              className="btn btn-ghost"
              onClick={() => deleteModalRef.current?.close()}
              disabled={actionLoading}
            >
              Cancel
            </button>
            
            {selectedNewOwner && (
              <button 
                className="btn btn-warning"
                onClick={handleTransferOwnership}
                disabled={actionLoading}
              >
                {actionLoading ? (
                  <>
                    <div className="loading loading-spinner loading-sm mr-2"></div>
                    Transferring...
                  </>
                ) : (
                  <>
                    <UserCheck className="h-4 w-4 mr-2" />
                    Transfer Ownership
                  </>
                )}
              </button>
            )}
            
            <button 
              className="btn btn-error"
              onClick={handleDeleteOrganization}
              disabled={actionLoading}
            >
              {actionLoading ? (
                <>
                  <div className="loading loading-spinner loading-sm mr-2"></div>
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Organization
                </>
              )}
            </button>
          </div>
        </div>
        
        <form method="dialog" className="modal-backdrop">
          <button onClick={() => deleteModalRef.current?.close()}>close</button>
        </form>
      </dialog>

    </>
  );
}