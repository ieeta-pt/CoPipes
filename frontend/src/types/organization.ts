export interface Organization {
  id: string;
  name: string;
  description?: string;
  created_at: string;
  owner_id: string;
  member_count: number;
}

export interface OrganizationMember {
  user_id: string;
  email: string;
  full_name?: string;
  role: OrganizationRole;
  joined_at: string;
  invited_by: string;
}

export interface OrganizationCreateRequest {
  name: string;
  description?: string;
}

export interface InviteUserRequest {
  email: string;
  role: OrganizationRole;
}

export enum OrganizationRole {
  OWNER = 'owner',
  ADMIN = 'admin',
  MANAGER = 'manager',
  MEMBER = 'member',
  VIEWER = 'viewer'
}

export interface RolePermissions {
  canManageMembers: boolean;
  canManageAdmins: boolean;
  canDeleteOrganization: boolean;
  canTransferOwnership: boolean;
  canCreateWorkflows: boolean;
  canViewWorkflows: boolean;
  canManageOrganizationSettings: boolean;
}

export const getRolePermissions = (role: OrganizationRole): RolePermissions => {
  const roleHierarchy = {
    [OrganizationRole.OWNER]: 5,
    [OrganizationRole.ADMIN]: 4,
    [OrganizationRole.MANAGER]: 3,
    [OrganizationRole.MEMBER]: 2,
    [OrganizationRole.VIEWER]: 1
  };

  const level = roleHierarchy[role] || 0;

  return {
    canManageMembers: [OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.MANAGER].includes(role),
    canManageAdmins: [OrganizationRole.OWNER, OrganizationRole.ADMIN].includes(role),
    canDeleteOrganization: role === OrganizationRole.OWNER,
    canTransferOwnership: role === OrganizationRole.OWNER,
    canCreateWorkflows: level >= 2, // Member and above
    canViewWorkflows: level >= 1, // All roles
    canManageOrganizationSettings: [OrganizationRole.OWNER, OrganizationRole.ADMIN].includes(role)
  };
};

export const canManageUser = (managerRole: OrganizationRole, targetRole: OrganizationRole): boolean => {
  const roleHierarchy = {
    [OrganizationRole.OWNER]: 5,
    [OrganizationRole.ADMIN]: 4,
    [OrganizationRole.MANAGER]: 3,
    [OrganizationRole.MEMBER]: 2,
    [OrganizationRole.VIEWER]: 1
  };

  const managerLevel = roleHierarchy[managerRole] || 0;
  const targetLevel = roleHierarchy[targetRole] || 0;

  return managerLevel > targetLevel;
};

export const getRoleDisplayName = (role: OrganizationRole): string => {
  const displayNames = {
    [OrganizationRole.OWNER]: 'Owner',
    [OrganizationRole.ADMIN]: 'Admin',
    [OrganizationRole.MANAGER]: 'Manager',
    [OrganizationRole.MEMBER]: 'Member',
    [OrganizationRole.VIEWER]: 'Viewer'
  };

  return displayNames[role] || role;
};

export const getRoleDescription = (role: OrganizationRole): string => {
  const descriptions = {
    [OrganizationRole.OWNER]: 'Full control over organization, can transfer ownership and delete organization',
    [OrganizationRole.ADMIN]: 'Can manage members and organization settings, cannot delete organization',
    [OrganizationRole.MANAGER]: 'Can invite/remove members, manage workflow permissions within teams',
    [OrganizationRole.MEMBER]: 'Standard access to organization workflows, can create personal workflows',
    [OrganizationRole.VIEWER]: 'Read-only access to organization workflows, cannot create or modify workflows'
  };

  return descriptions[role] || role;
};

export interface UserOrganizationInfo {
  organization_id: string;
  organization_name: string;
  role: OrganizationRole;
}