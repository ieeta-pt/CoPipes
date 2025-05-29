import { WorkflowRequest } from "@/components/airflow-tasks/types"

export async function submitWorkflow(payload: WorkflowRequest) {
  console.log("submitWorkflow payload:", payload);
  
  const res = await fetch("/api/workflows/new", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })

  console.log("submitWorkflow response:", res.status, res.statusText);

  if (!res.ok) {
    let errorMessage = "Failed to submit workflow";
    try {
      const errorData = await res.json();
      console.error("API Error Details:", errorData);
      errorMessage = errorData.detail || errorData.message || errorMessage;
      if (errorData.detail && Array.isArray(errorData.detail)) {
        errorMessage = errorData.detail.map((err: any) => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
      }
    } catch (e) {
      console.error("Failed to parse error response");
    }
    throw new Error(errorMessage);
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

export async function executeWorkflow(name: string, payload: WorkflowRequest) {
  name = name.replace(/ /g, "_");
  console.log("executeWorkflow", name, payload)
  const res = await fetch(`/api/workflows/execute/${name}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    let errorMessage = "Failed to execute workflow";
    try {
      const errorData = await res.json();
      errorMessage = errorData.detail || errorData.message || errorMessage;
      console.error("API Error:", errorData);
    } catch (e) {
      console.error("Failed to parse error response");
    }
    throw new Error(errorMessage);
  }

  return res.json();
}