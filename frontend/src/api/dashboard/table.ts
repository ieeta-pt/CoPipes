// lib/api/getWorkflows.ts

import { Workflow } from "@/app/dashboard/columns"; 
import { apiClient } from "@/services/api";

export async function getWorkflows(): Promise<Workflow[]> {
  return apiClient.get("/api/workflows/all");
}

export async function deleteWorkflowAPI(name: string): Promise<void> {
  name = name.replace(/ /g, "_");
  console.log("deleteWorkflowAPI", name);
  return apiClient.delete(`/api/workflows/${name}`);
}

export async function downloadWorkflowAPI(name: string): Promise<any> {
  name = name.replace(/ /g, "_");
  console.log("downloadWorkflowAPI", name);
  return apiClient.get(`/api/workflows/${name}`);
}

export async function uploadWorkflowAPI(file: File): Promise<any> {
  return apiClient.uploadFile("/api/workflows/upload", file);
}
