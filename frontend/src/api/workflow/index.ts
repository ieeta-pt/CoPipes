import { WorkflowRequest } from "@/components/airflow-tasks/types";

// Mock data for testing
const MOCK_WORKFLOW = {
  dag_id: "test_workflow",
  tasks: [
    {
      id: "python_1",
      content: "PythonOperator",
      type: "operator",
      subtype: "python",
      config: [
        { name: "task_id", value: "print_hello", type: "string" },
        { name: "python_callable", value: "print('Hello World!')", type: "code" },
      ],
    },
    {
      id: "bash_1",
      content: "BashOperator",
      type: "operator",
      subtype: "bash",
      config: [
        { name: "task_id", value: "list_files", type: "string" },
        { name: "bash_command", value: "ls -la", type: "string" },
      ],
    },
  ],
};

export async function getWorkflow(id: string) {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 1500));
  
  if (id === "test") {
    return MOCK_WORKFLOW;
  }
  
  throw new Error("Workflow not found");
}

export async function submitWorkflow(payload: WorkflowRequest) {
  const res = await fetch("/app/workflows/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    console.error("Error submitting workflow:", res.statusText);
    throw new Error("Failed to submit workflow");
  }

  return res.json();
}

// export async function getWorkflow(id: string) {
//   const res = await fetch(`/workflows/${id}`);

//   if (!res.ok) {
//     throw new Error("Failed to fetch workflow");
//   }

//   return res.json();
// }