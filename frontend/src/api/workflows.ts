import { apiClient } from '@/services/api';
import { 
  Workflow, 
  WorkflowCollaborator, 
  AddCollaboratorRequest, 
  UpdateCollaboratorRequest 
} from '@/types/workflow';

export const workflowApi = {
  // Get all user workflows
  async getUserWorkflows(): Promise<Workflow[]> {
    return apiClient.get('/api/workflows/all');
  },

  // Get specific workflow
  async getWorkflow(workflowName: string): Promise<any> {
    return apiClient.get(`/api/workflows/${workflowName.replace(/ /g, '_')}`);
  },

  // Create new workflow
  async createWorkflow(workflowData: any): Promise<any> {
    return apiClient.post('/api/workflows/new', workflowData);
  },

  // Update workflow
  async updateWorkflow(workflowName: string, workflowData: any): Promise<any> {
    return apiClient.put(`/api/workflows/${workflowName.replace(/ /g, '_')}`, workflowData);
  },

  // Delete workflow
  async deleteWorkflow(workflowName: string): Promise<{ message: string }> {
    return apiClient.delete(`/api/workflows/${workflowName.replace(/ /g, '_')}`);
  },

  // Execute workflow
  async executeWorkflow(workflowData: any): Promise<any> {
    return apiClient.post(`/api/workflows/execute/${workflowData.dag_id}`, workflowData);
  },

  // Copy/fork workflow
  async copyWorkflow(workflowName: string): Promise<any> {
    return apiClient.post(`/api/workflows/${workflowName.replace(/ /g, '_')}/copy`);
  },

  // Enhanced collaborator management
  async getEnhancedCollaborators(workflowName: string): Promise<{ workflow_name: string; collaborators: WorkflowCollaborator[]; permissions: any }> {
    return apiClient.get(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators/enhanced`);
  },

  async addEnhancedCollaborator(workflowName: string, request: AddCollaboratorRequest): Promise<{ message: string }> {
    return apiClient.post(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators/enhanced`, request);
  },

  async updateCollaboratorRole(workflowName: string, email: string, request: UpdateCollaboratorRequest): Promise<{ message: string }> {
    return apiClient.put(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators/${encodeURIComponent(email)}/role`, request);
  },

  async removeEnhancedCollaborator(workflowName: string, email: string): Promise<{ message: string }> {
    return apiClient.delete(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators/enhanced/${encodeURIComponent(email)}`);
  },

  // Legacy collaborator management (for backward compatibility)
  async getCollaborators(workflowName: string): Promise<{ workflow_name: string; collaborators: string[]; permissions: any }> {
    return apiClient.get(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators`);
  },

  async addCollaborator(workflowName: string, email: string): Promise<{ message: string }> {
    return apiClient.post(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators`, { email });
  },

  async removeCollaborator(workflowName: string, email: string): Promise<{ message: string }> {
    return apiClient.delete(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators/${encodeURIComponent(email)}`);
  },

  // Workflow execution and history
  async getWorkflowRuns(workflowName: string): Promise<{ runs: any[] }> {
    return apiClient.get(`/api/workflows/${workflowName.replace(/ /g, '_')}/runs`);
  },

  async getWorkflowRunDetails(workflowName: string, runId: string): Promise<any> {
    return apiClient.get(`/api/workflows/${workflowName.replace(/ /g, '_')}/runs/${runId}`);
  },

  // Organization workflows
  async getOrganizationWorkflows(orgId: string): Promise<{ workflows: Workflow[]; organization_id: string }> {
    return apiClient.get(`/api/workflows/organization/${orgId}`);
  },

  async createOrganizationWorkflow(orgId: string, workflowData: any): Promise<any> {
    return apiClient.post(`/api/workflows/organization/${orgId}/new`, workflowData);
  },

  // File upload
  async uploadWorkflow(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post('/api/workflows/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};