import { WorkflowRequest } from "@/components/airflow-tasks/types"

export async function submitWorkflow(payload: WorkflowRequest) {
  const res = await fetch("/api/workflows/new", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  console.log("submitWorkflow", payload, res)

  if (!res.ok) {
    throw new Error("Failed to submit workflow")
  }

  return res.json()
}

export async function getWorkflow(name: string) {
  name = name.replace(/ /g, "_");
  console.log("getWorkflow", name)
  const res = await fetch(`/api/workflows/${name}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    }
  });

  if (!res.ok) {
    throw new Error("Failed to fetch workflow");
  }

  return res.json();
}

export async function updateWorkflow(name: string, payload: WorkflowRequest) {
  name = name.replace(/ /g, "_");
  console.log("updateWorkflow", name) 
  try {
    const res = await fetch(`/api/workflows/${name}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errorDetails = await res.json();
      throw new Error(`Failed to update workflow: ${errorDetails.message || res.statusText}`);
    }

    return res.json();
  } catch (error) {
    console.error("Error updating workflow:", error);
    throw new Error("An unexpected error occurred while updating the workflow.");
  }
} 