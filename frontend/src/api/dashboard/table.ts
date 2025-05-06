// lib/api/getWorkflows.ts

import { Workflow } from "@/app/dashboard/columns"; 

export async function getWorkflows(): Promise<Workflow[]> {
  const res = await fetch("/api/get_dags", {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store", 
  });

  if (!res.ok) {
    throw new Error("Failed to fetch workflows");
  }

  return res.json();
}
