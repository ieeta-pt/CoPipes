import { WorkflowRequest } from "@/components/airflow-tasks/types"
import { apiClient } from "@/services/api"

export async function submitWorkflow(payload: WorkflowRequest) {
  console.log("submitWorkflow payload:", payload);
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