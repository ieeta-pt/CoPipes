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
  ADMIN = 'admin',
  MEMBER = 'member'
}

export interface UserOrganizationInfo {
  organization_id: string;
  organization_name: string;
  role: OrganizationRole;
}