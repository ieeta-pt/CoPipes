"use client";

import { useEffect, useState } from "react";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { executeWorkflow, getWorkflow } from "@/api/workflow/test";
import { Registry } from "@/components/airflow-tasks/Registry";
import { LogsPanel } from "@/components/workflow/LogsPanel";
import { ExecutableTask } from "./ExecutableTask";
import { Play } from "lucide-react";
import { run } from "node:test";
import { ConfigSidebar } from "../ConfigSidebar";

function getColorForType(type: string): string {
  const colors: Record<string, string> = {
    Extraction: "#3b82f6",
    Transformation: "#10b981",
    Loading: "#f59e0b",
    Analysis: "#8b5cf6",
    General: "#6b7280",
  };
  return colors[type] || "#6b7280";
}

export default function WorkflowExecute({
  workflowId,
}: {
  workflowId?: string;
}) {
  const [workflow, setWorkflow] = useState<WorkflowComponent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState("");
  const [output, setOutput] = useState("");

  useEffect(() => {
    async function fetchWorkflow() {
      if (workflowId) {
        try {
          setIsLoading(true);
          setError(null);
          const workflow = await getWorkflow(workflowId);
          setWorkflowName(workflow.dag_id.replace(/_/g, " "));
          console.log("Fetched workflow:", workflow.dag_id);
          setWorkflow(
            workflow.tasks.map((task: any) => ({
              ...task,
              config: task.config.map((field: any) => ({
                ...field,
                name: field.name,
                value: field.value,
                type: field.type,
              })),
            }))
          );
        } catch (error) {
          setError(
            "Failed to fetch workflow. It might have been deleted or you don't have permission to view it."
          );
          console.error(error);
        } finally {
          setIsLoading(false);
        }
      }
    }
    fetchWorkflow();
  }, [workflowId]);

  async function runWorkflow() {
    if (!workflowId) return;

    

    try {
      const payload = {
        dag_id: workflowId.replace(/ /g, "_"),
        tasks: workflow.map((task) => ({
          id: task.id,
          type: task.type,
          content: task.content,
          config: task.config.map((field) => ({
            name: field.name,
            value: field.value,
            type: field.type,
          })),
        })),
      };

      const result = await executeWorkflow(workflowId, payload);
      setOutput(result.output);
    } catch (error) {
      console.error("Error executing workflow:", error);
      setOutput(
        "Failed to execute workflow. Please check the console for details."
      );
    }
  }

  const handleTaskUpdate = (taskId: string, newConfig: any) => {
    setWorkflow((prevWorkflow) =>
      prevWorkflow.map((task) =>
        task.id === taskId ? { ...task, config: newConfig } : task
      )
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="loading loading-spinner loading-lg"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="alert alert-error max-w-lg">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="stroke-current shrink-0 h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 h-[calc(100vh-4rem)] p-4 gap-4">
      {/* Main content */}
      <div className="flex flex-1 gap-4">
        <div className="flex flex-col gap-4">
          <ConfigSidebar />
        </div>

        {/* Left: Input + Tasks */}
        <div className="flex flex-col flex-1 gap-4">
          <div className="flex justify-between">
            <input
              id="workflowName"
              name="workflowName"
              type="text"
              placeholder="Nameless workflow"
              className="input w-full max-w-md text-lg"
              value={workflowName}
              readOnly={true}
            />
            <button className="btn btn-primary text-white" onClick={runWorkflow}>
              <Play className="h-4 w-4 mr-2" /> Execute
            </button>
          </div>

          <section className="flex-1">
            {/* Full height container */}

            <div className="flex flex-col h-full bg-base-100">
              {/* Scrollable area */}
              <div className="flex-1 space-y-4">
                {workflow.length === 0 ? (
                  <div className="flex items-center rounded-lg border-2 border-dashed border-base-200 justify-center h-full text-gray-500">
                    No tasks in this workflow.
                  </div>
                ) : (
                  workflow.map((task) => (
                    <div
                      key={task.id}
                      className="card bg-base-100 shadow-md mb-2"
                      style={{
                        borderLeft: `4px solid ${getColorForType(task.type)}`,
                      }}
                    >
                      <div className="card-body p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div className="text-lg font-semibold">
                            {task.content}
                          </div>
                          <div
                            className="flex gap-2 badge text-md"
                            style={{
                              backgroundColor: getColorForType(task.type),
                              color: "white",
                            }}
                          >
                            {task.type}
                          </div>
                        </div>
                        <ExecutableTask
                          config={task.config}
                          onUpdate={(newConfig) =>
                            handleTaskUpdate(task.id, newConfig)
                          }
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>
        </div>

        {/* Right: Logs */}
        {/* <LogsPanel output={output} /> */}
      </div>
    </div>
  );
}
