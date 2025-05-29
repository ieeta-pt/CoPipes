// lib/api/getWorkflows.ts

import { Workflow } from "@/app/dashboard/columns"; 

export async function getWorkflows(): Promise<Workflow[]> {
  const res = await fetch("/api/workflows/all", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store", 
  });

  if (!res.ok) {
    throw new Error("Failed to fetch workflows");
  }

  console.log("Response from API:", res);

  return res.json();
}

export async function editWorkflowAPI(name: string): Promise<void> {
  name = name.replace(/ /g, "_");
  console.log("editWorkflowAPI", name);
  const res = await fetch(`/api/workflows/${name}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error("Failed to get workflow");
  }

  console.log("Response from API:", res);
}

export async function deleteWorkflowAPI(name: string): Promise<void> {
  name = name.replace(/ /g, "_");
  console.log("deleteWorkflowAPI", name);
  const res = await fetch(`/api/workflows/${name}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error("Failed to delete workflow");
  }

  console.log("Response from API:", res);
}

export async function downloadWorkflowAPI(name: string): Promise<any> {
  name = name.replace(/ /g, "_");
  console.log("downloadWorkflowAPI", name);
  const res = await fetch(`/api/workflows/${name}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch workflow");
  }

  return res.json();
}

export async function uploadWorkflowAPI(file: File): Promise<any> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("/api/workflows/upload", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Failed to upload workflow");
  }

  return res.json();
}
