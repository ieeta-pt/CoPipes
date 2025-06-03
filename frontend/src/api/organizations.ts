import { 
  Organization, 
  OrganizationMember, 
  OrganizationCreateRequest, 
  InviteUserRequest,
  OrganizationRole 
} from '@/types/organization';
import { apiClient } from '@/services/api';

export const organizationApi = {
  // Create a new organization
  async createOrganization(data: OrganizationCreateRequest): Promise<Organization> {
    return apiClient.post('/api/organizations/', data);
  },

  // Get user's organizations
  async getUserOrganizations(): Promise<Organization[]> {
    return apiClient.get('/api/organizations/');
  },

  // Get organization members (admin only)
  async getOrganizationMembers(orgId: string): Promise<OrganizationMember[]> {
    return apiClient.get(`/api/organizations/${orgId}/members`);
  },

  // Invite user to organization (admin only)
  async inviteUser(orgId: string, data: InviteUserRequest): Promise<{ message: string }> {
    return apiClient.post(`/api/organizations/${orgId}/invite`, data);
  },

  // Remove user from organization (admin only)
  async removeUser(orgId: string, userId: string): Promise<{ message: string }> {
    return apiClient.delete(`/api/organizations/${orgId}/members/${userId}`);
  },

  // Update user role (admin only)
  async updateUserRole(orgId: string, userId: string, role: OrganizationRole): Promise<{ message: string }> {
    return apiClient.put(`/api/organizations/${orgId}/members/${userId}/role`, { role });
  },

  // Get user role in organization
  async getUserRole(orgId: string): Promise<{ role: OrganizationRole }> {
    return apiClient.get(`/api/organizations/${orgId}/role`);
  },

  // Delete organization (owner only)
  async deleteOrganization(orgId: string): Promise<{ message: string }> {
    return apiClient.delete(`/api/organizations/${orgId}`);
  },

  // Get organization workflows
  async getOrganizationWorkflows(orgId: string): Promise<{ workflows: any[], organization_id: string }> {
    return apiClient.get(`/api/workflows/organization/${orgId}`);
  },

  // Create organization workflow
  async createOrganizationWorkflow(orgId: string, workflowData: any): Promise<any> {
    return apiClient.post(`/api/workflows/organization/${orgId}/new`, workflowData);
  },
};