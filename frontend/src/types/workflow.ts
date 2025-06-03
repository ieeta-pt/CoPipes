export enum WorkflowRole {
  OWNER = 'owner',
  EDITOR = 'editor',
  EXECUTOR = 'executor',
  VIEWER = 'viewer',
  ANALYST = 'analyst'
}

export interface WorkflowPermissions {
  role: WorkflowRole;
  is_owner: boolean;
  can_view: boolean;
  can_edit: boolean;
  can_execute: boolean;
  can_download: boolean;
  can_copy: boolean;
  can_delete: boolean;
  can_manage_permissions: boolean;
  can_view_sensitive_data: boolean;
}

export interface WorkflowCollaborator {
  email: string;
  role: WorkflowRole;
  is_owner: boolean;
  invited_at?: string | null;
  invited_by?: string | null;
}

export interface AddCollaboratorRequest {
  email: string;
  role: WorkflowRole;
}

export interface UpdateCollaboratorRequest {
  role: WorkflowRole;
}

export interface Workflow {
  id: string;
  name: string;
  last_edit: string;
  user_id: string;
  organization_id?: string | null;
  last_run?: string | null;
  status: string;
  collaborators: string[]; // Legacy
  workflow_collaborators?: WorkflowCollaborator[]; // Enhanced
  permissions: WorkflowPermissions;
  role: string; // User's relationship to workflow
  owner_email: string;
  owner_name?: string;
  organization_name?: string;
}

export const getRolePermissions = (role: WorkflowRole): Partial<WorkflowPermissions> => {
  const roleHierarchy = {
    [WorkflowRole.OWNER]: 5,
    [WorkflowRole.EDITOR]: 4,
    [WorkflowRole.EXECUTOR]: 3,
    [WorkflowRole.ANALYST]: 2,
    [WorkflowRole.VIEWER]: 1
  };

  const level = roleHierarchy[role] || 0;

  return {
    can_view: true, // All roles can view
    can_edit: [WorkflowRole.OWNER, WorkflowRole.EDITOR].includes(role),
    can_execute: [WorkflowRole.OWNER, WorkflowRole.EDITOR, WorkflowRole.EXECUTOR].includes(role),
    can_download: true, // All roles can download
    can_copy: [WorkflowRole.OWNER, WorkflowRole.EDITOR, WorkflowRole.ANALYST].includes(role),
    can_delete: role === WorkflowRole.OWNER,
    can_manage_permissions: role === WorkflowRole.OWNER,
    can_view_sensitive_data: [WorkflowRole.OWNER, WorkflowRole.EDITOR, WorkflowRole.EXECUTOR].includes(role)
  };
};

export const getRoleDisplayName = (role: WorkflowRole): string => {
  const displayNames = {
    [WorkflowRole.OWNER]: 'Owner',
    [WorkflowRole.EDITOR]: 'Editor',
    [WorkflowRole.EXECUTOR]: 'Executor',
    [WorkflowRole.ANALYST]: 'Analyst',
    [WorkflowRole.VIEWER]: 'Viewer'
  };

  return displayNames[role] || role;
};

export const getRoleDescription = (role: WorkflowRole): string => {
  const descriptions = {
    [WorkflowRole.OWNER]: 'Full control over workflow, can modify and manage permissions',
    [WorkflowRole.EDITOR]: 'Can modify workflow structure and configuration, cannot manage permissions',
    [WorkflowRole.EXECUTOR]: 'Can run workflows and view results, cannot modify workflow',
    [WorkflowRole.ANALYST]: 'Can view workflows and create copies/forks for experimentation',
    [WorkflowRole.VIEWER]: 'Read-only access to workflow design and results'
  };

  return descriptions[role] || role;
};

export const getRoleColor = (role: WorkflowRole): string => {
  const colors = {
    [WorkflowRole.OWNER]: 'badge-primary',
    [WorkflowRole.EDITOR]: 'badge-secondary',
    [WorkflowRole.EXECUTOR]: 'badge-accent',
    [WorkflowRole.ANALYST]: 'badge-info',
    [WorkflowRole.VIEWER]: 'badge-ghost'
  };

  return colors[role] || 'badge-neutral';
};

export const canManageCollaborator = (userRole: WorkflowRole, targetRole: WorkflowRole): boolean => {
  const roleHierarchy = {
    [WorkflowRole.OWNER]: 5,
    [WorkflowRole.EDITOR]: 4,
    [WorkflowRole.EXECUTOR]: 3,
    [WorkflowRole.ANALYST]: 2,
    [WorkflowRole.VIEWER]: 1
  };

  const userLevel = roleHierarchy[userRole] || 0;
  const targetLevel = roleHierarchy[targetRole] || 0;

  // Only owners can manage permissions, and cannot manage other owners
  return userRole === WorkflowRole.OWNER && targetRole !== WorkflowRole.OWNER;
};