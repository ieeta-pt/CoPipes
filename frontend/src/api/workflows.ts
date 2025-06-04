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

  // Create new workflow (with organization support)
  async createWorkflow(workflowData: any, organizationId?: string | null): Promise<any> {
    if (organizationId) {
      return apiClient.post(`/api/workflows/organization/${organizationId}/new`, workflowData);
    }
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

  //  collaborator management
  async getCollaborators(workflowName: string): Promise<{ workflow_name: string; collaborators: WorkflowCollaborator[]; permissions: any }> {
    return apiClient.get(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators`);
  },

  async addCollaborator(workflowName: string, request: AddCollaboratorRequest): Promise<{ message: string }> {
    return apiClient.post(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators`, request);
  },

  async updateCollaboratorRole(workflowName: string, email: string, request: UpdateCollaboratorRequest): Promise<{ message: string }> {
    return apiClient.put(`/api/workflows/${workflowName.replace(/ /g, '_')}/collaborators/${encodeURIComponent(email)}/role`, request);
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

  // File upload
  async uploadWorkflow(file: File): Promise<any> {
    return apiClient.uploadFile('/api/workflows/upload', file);
  },

  // General file upload for tasks
  async uploadFile(file: File): Promise<any> {
    return apiClient.uploadFile('/api/workflows/file_input', file);
  },
};

// Legacy function aliases for backward compatibility
export const getWorkflows = workflowApi.getUserWorkflows;
export const deleteWorkflowAPI = workflowApi.deleteWorkflow;
export const downloadWorkflowAPI = workflowApi.getWorkflow;
export const uploadWorkflowAPI = workflowApi.uploadWorkflow;
export const copyWorkflowAPI = workflowApi.copyWorkflow;
export const submitWorkflow = workflowApi.createWorkflow;
export const getWorkflow = workflowApi.getWorkflow;
export const updateWorkflow = workflowApi.updateWorkflow;
export const executeWorkflow = workflowApi.executeWorkflow;
export const getWorkflowRuns = workflowApi.getWorkflowRuns;
export const getWorkflowRunDetails = workflowApi.getWorkflowRunDetails;