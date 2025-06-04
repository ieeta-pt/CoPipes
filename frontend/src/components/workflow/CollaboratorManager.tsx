"use client";

import { useState, useEffect } from "react";
import { Plus, Trash2, Users, Edit } from "lucide-react";
import { workflowApi } from "@/api/workflows";
import { 
  WorkflowRole, 
  WorkflowCollaborator, 
  AddCollaboratorRequest, 
  UpdateCollaboratorRequest,
  getRoleDisplayName,
  getRoleDescription,
  getRoleColor,
  canManageCollaborator
} from "@/types/workflow";

interface CollaboratorManagerProps {
  workflowName: string;
  collaborators: WorkflowCollaborator[];
  userRole: WorkflowRole;
  canManagePermissions: boolean;
  onCollaboratorsChange?: (collaborators: WorkflowCollaborator[]) => void;
}

export default function CollaboratorManager({
  workflowName,
  collaborators,
  userRole,
  canManagePermissions,
  onCollaboratorsChange,
}: CollaboratorManagerProps) {
  const [localCollaborators, setLocalCollaborators] = useState<WorkflowCollaborator[]>(
    Array.isArray(collaborators) ? collaborators : []
  );
  const [newCollaboratorEmail, setNewCollaboratorEmail] = useState("");
  const [newCollaboratorRole, setNewCollaboratorRole] = useState<WorkflowRole>(WorkflowRole.VIEWER);
  const [editingCollaborator, setEditingCollaborator] = useState<string | null>(null);
  const [editingRole, setEditingRole] = useState<WorkflowRole>(WorkflowRole.VIEWER);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLocalCollaborators(Array.isArray(collaborators) ? collaborators : []);
  }, [collaborators]);

  const addCollaborator = async () => {
    if (!newCollaboratorEmail.trim()) return;
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(newCollaboratorEmail.trim())) {
      setError("Please enter a valid email address");
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      const request: AddCollaboratorRequest = {
        email: newCollaboratorEmail.trim(),
        role: newCollaboratorRole
      };

      await workflowApi.addCollaborator(workflowName, request);

      // Refresh collaborators list
      await fetchCollaborators();
      setNewCollaboratorEmail("");
      setNewCollaboratorRole(WorkflowRole.VIEWER);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add collaborator");
    } finally {
      setIsLoading(false);
    }
  };

  const updateCollaboratorRole = async (email: string, newRole: WorkflowRole) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const request: UpdateCollaboratorRequest = { role: newRole };

      await workflowApi.updateCollaboratorRole(workflowName, email, request);

      // Refresh collaborators list
      await fetchCollaborators();
      setEditingCollaborator(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update collaborator role");
    } finally {
      setIsLoading(false);
    }
  };

  const removeCollaborator = async (email: string) => {
    if (!confirm(`Are you sure you want to remove ${email} from this workflow?`)) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    try {
      await workflowApi.removeCollaborator(workflowName, email);

      // Refresh collaborators list
      await fetchCollaborators();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to remove collaborator");
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCollaborators = async () => {
    try {
      const data = await workflowApi.getCollaborators(workflowName);
      setLocalCollaborators(data.collaborators);
      onCollaboratorsChange?.(data.collaborators);
    } catch (err) {
      console.error("Failed to fetch collaborators:", err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      addCollaborator();
    }
  };

  const startEditing = (collaborator: WorkflowCollaborator) => {
    setEditingCollaborator(collaborator.email);
    setEditingRole(collaborator.role);
  };

  const cancelEditing = () => {
    setEditingCollaborator(null);
    setEditingRole(WorkflowRole.VIEWER);
  };

  const saveRoleChange = () => {
    if (editingCollaborator) {
      updateCollaboratorRole(editingCollaborator, editingRole);
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center gap-2 mb-4">
        <Users className="h-5 w-5 text-primary" />
        <h3 className="text-lg font-semibold">Collaborators</h3>
        <span className="badge badge-neutral">{localCollaborators.length}</span>
      </div>

      {error && (
        <div className={`alert mb-4 ${
          error.includes("not registered") ? "alert-info" : "alert-error"
        }`}>
          <div className="flex flex-col">
            <span className="font-medium">
              {error.includes("not registered") ? "User Not Found" : "Error"}
            </span>
            <span className="text-sm mt-1">{error}</span>
          </div>
        </div>
      )}

      {/* Add new collaborator */}
      {canManagePermissions && (
        <div className="mb-4 p-4 bg-base-100 rounded-lg border border-base-300">
          <h4 className="font-medium mb-3">Invite New Collaborator</h4>
          <div className="space-y-3">
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="Enter collaborator email"
                className="input input-bordered flex-1"
                value={newCollaboratorEmail}
                onChange={(e) => setNewCollaboratorEmail(e.target.value)}
                onKeyDown={handleKeyPress}
                disabled={isLoading}
              />
            </div>
            
            <div className="flex gap-2 items-end">
              <div className="flex-1">
                <label className="label">
                  <span className="label-text">Role</span>
                </label>
                <select
                  className="select select-bordered w-full"
                  value={newCollaboratorRole}
                  onChange={(e) => setNewCollaboratorRole(e.target.value as WorkflowRole)}
                  disabled={isLoading}
                >
                  <option value={WorkflowRole.VIEWER}>Viewer</option>
                  <option value={WorkflowRole.ANALYST}>Analyst</option>
                  <option value={WorkflowRole.EXECUTOR}>Executor</option>
                  <option value={WorkflowRole.EDITOR}>Editor</option>
                </select>
                <label className="label">
                  <span className="label-text-alt text-xs">
                    {getRoleDescription(newCollaboratorRole)}
                  </span>
                </label>
              </div>
              
              <button
                className="btn btn-primary"
                onClick={addCollaborator}
                disabled={isLoading || !newCollaboratorEmail.trim()}
              >
                {isLoading ? (
                  <span className="loading loading-spinner loading-sm"></span>
                ) : (
                  <Plus className="h-4 w-4" />
                )}
                Invite
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Collaborators list */}
      <div className="space-y-2">
        {localCollaborators.length === 0 ? (
          <p className="text-base-content/50 text-center py-8">
            No collaborators added yet.
            {canManagePermissions && (
              <span className="block text-sm mt-1">
                Use the form above to invite team members.
              </span>
            )}
          </p>
        ) : (
          localCollaborators.map((collaborator) => (
            <div
              key={collaborator.email}
              className="flex items-center justify-between p-4 bg-base-100 rounded-lg border border-base-300"
            >
              <div className="flex-1">
                <div className="flex items-center gap-3">
                  <span className="font-medium">{collaborator.email}</span>
                  {collaborator.is_owner && (
                    <span className="badge badge-primary">Owner</span>
                  )}
                </div>
                <div className="flex items-center gap-2 mt-1">
                  {editingCollaborator === collaborator.email ? (
                    <div className="flex items-center gap-2">
                      <select
                        className="select select-bordered select-sm"
                        value={editingRole}
                        onChange={(e) => setEditingRole(e.target.value as WorkflowRole)}
                        disabled={isLoading}
                      >
                        <option value={WorkflowRole.VIEWER}>Viewer</option>
                        <option value={WorkflowRole.ANALYST}>Analyst</option>
                        <option value={WorkflowRole.EXECUTOR}>Executor</option>
                        <option value={WorkflowRole.EDITOR}>Editor</option>
                      </select>
                      <button
                        className="btn btn-success btn-sm"
                        onClick={saveRoleChange}
                        disabled={isLoading}
                      >
                        Save
                      </button>
                      <button
                        className="btn btn-ghost btn-sm"
                        onClick={cancelEditing}
                        disabled={isLoading}
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <>
                      <span className={`badge ${getRoleColor(collaborator.role)}`}>
                        {getRoleDisplayName(collaborator.role)}
                      </span>
                      {collaborator.invited_at && (
                        <span className="text-xs text-base-content/60">
                          Joined {new Date(collaborator.invited_at).toLocaleDateString()}
                        </span>
                      )}
                    </>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2">
                {canManagePermissions && 
                 canManageCollaborator(userRole, collaborator.role) && 
                 !collaborator.is_owner && 
                 editingCollaborator !== collaborator.email && (
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => startEditing(collaborator)}
                    disabled={isLoading}
                    title="Edit role"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                )}
                
                {canManagePermissions && 
                 canManageCollaborator(userRole, collaborator.role) && 
                 !collaborator.is_owner && (
                  <button
                    className="btn btn-ghost btn-sm text-error hover:bg-error hover:text-error-content"
                    onClick={() => removeCollaborator(collaborator.email)}
                    disabled={isLoading}
                    title="Remove collaborator"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {!canManagePermissions && (
        <div className="mt-4 p-3 bg-base-200 rounded-lg">
          <p className="text-sm text-base-content/70">
            <strong>Your role:</strong> {getRoleDisplayName(userRole)}
          </p>
          <p className="text-xs text-base-content/60 mt-1">
            {getRoleDescription(userRole)}
          </p>
          {userRole !== WorkflowRole.OWNER && (
            <p className="text-xs text-base-content/50 mt-2">
              Only the workflow owner can manage collaborators and permissions.
            </p>
          )}
        </div>
      )}
    </div>
  );
}