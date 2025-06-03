import { WorkflowRequest } from "@/components/airflow-tasks/types"
import { apiClient } from "@/services/api"

export async function submitWorkflow(payload: WorkflowRequest, organizationId?: string | null) {
  console.log("submitWorkflow payload:", payload, "organizationId:", organizationId);
  
  // If organizationId is provided, use the organization-specific endpoint
  if (organizationId) {
    return apiClient.post(`/api/workflows/organization/${organizationId}/new`, payload);
  }
  
  // Otherwise use the regular personal workflow endpoint
  return apiClient.post("/api/workflows/new", payload);
}

export async function getWorkflow(name: string) {
  name = name.replace(/ /g, "_");
  console.log("getWorkflow", name);
  return apiClient.get(`/api/workflows/${name}`);
}

export async function updateWorkflow(name: string, payload: WorkflowRequest) {
  name = name.replace(/ /g, "_");
  console.log("updateWorkflow", name);
  return apiClient.put(`/api/workflows/${name}`, payload);
} 

export async function executeWorkflow(name: string, payload: WorkflowRequest) {
  name = name.replace(/ /g, "_");
  console.log("executeWorkflow", name, payload);
  return apiClient.post(`/api/workflows/execute/${name}`, payload);
}

export async function getWorkflowRuns(name: string) {
  name = name.replace(/ /g, "_");
  console.log("getWorkflowRuns", name);
  return apiClient.get(`/api/workflows/${name}/runs`);
}

export async function getWorkflowRunDetails(name: string, dagRunId: string) {
  name = name.replace(/ /g, "_");
  console.log("getWorkflowRunDetails", name, dagRunId);
  return apiClient.get(`/api/workflows/${name}/runs/${dagRunId}`);
}