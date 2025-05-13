// lib/api/getWorkflows.ts

import { Workflow } from "@/app/dashboard/columns"; 

export async function getWorkflows(): Promise<Workflow[]> {
  const res = await fetch("/api/workflows", {
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
  const res = await fetch(`/api/workflows/${name}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!res.ok) {
    throw new Error("Failed to edit workflow");
  }

  console.log("Response from API:", res);
}

export async function deleteWorkflowAPI(name: string): Promise<void> {
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
