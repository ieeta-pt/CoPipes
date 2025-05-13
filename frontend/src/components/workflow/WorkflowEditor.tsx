"use client";

import { useState, useEffect } from "react";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { Registry } from "@/components/airflow-tasks/Registry";
import { Sidebar } from "@/components/workflow/Sidebar";
import { LogsPanel } from "@/components/workflow/LogsPanel";
import { WorkflowCanvas } from "./WorkflowCanvas";
import { submitWorkflow, getWorkflow } from "@/api/workflow/index";
import { useRouter } from "next/navigation";


const createIdBuilder = (prefix = "id") => () =>
    `${prefix}_${Math.random().toString(36).substring(2, 5)}`;

export default function WorkflowEditor({ workflowId }: { workflowId?: string }) {
  const router = useRouter();
  const [workflowItems, setWorkflowItems] = useState<WorkflowComponent[]>([]);
  const [output, setOutput] = useState("");
  const [workflowName, setWorkflowName] = useState("");
  const [isLoading, setIsLoading] = useState(!!workflowId);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchWorkflow() {
      if (workflowId) {
        try {
          setIsLoading(true);
          setError(null);
          const workflow = await getWorkflow(workflowId);
          setWorkflowName(workflow.dag_id);
          setWorkflowItems(
            workflow.tasks.map((task: any) => ({
              ...task,
              config: task.config.map((field: any) => ({
                ...field,
                name: field.name || field.key,
              })),
            }))
          );
        } catch (error) {
          setError("Failed to fetch workflow. It might have been deleted or you don't have permission to view it.");
          console.error(error);
        } finally {
          setIsLoading(false);
        }
      }
    }

    fetchWorkflow();
  }, [workflowId]);

  const addComponent = (content: string) => {
    const taskDef = Registry[content];
    const newItem: WorkflowComponent = {
      id: createIdBuilder(content)(),
      content,
      type: taskDef.type,
      subtype: taskDef.subtype,
      config: [...taskDef.defaultConfig],
    };
    setWorkflowItems([...workflowItems, newItem]);
  };

  const compileWorkflow = async () => {
    if (!workflowName) {
      setOutput("❌ Workflow name is required");
      document.getElementById("workflowName")?.classList.add("input-error");
      return;
    }

    console.log("Compiling workflow with items:", workflowItems);

    const payload = {
      dag_id: workflowName,
      tasks: workflowItems,
    };

    try {
      setOutput("Compiling workflow...");
      const result = await submitWorkflow(payload);
      setOutput(JSON.stringify(result, null, 2));
    } catch (err) {
      console.error(err);
      setOutput("❌ Failed to compile workflow");
    }
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
          <svg xmlns="http://www.w3.org/2000/svg" className="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 h-[calc(100vh-4rem)] p-4 gap-4">
      {/* Sidebar stays outside this block */}
      <Sidebar onAddComponent={addComponent} />

      <div className="flex flex-1 gap-4">
        {/* Left: Input + Canvas */}
        <div className="flex flex-col flex-1 gap-4">
          <div>
            <input
              id="workflowName"
              name="workflowName"
              type="text"
              placeholder="Nameless workflow"
              className="input input-bordered w-full max-w-md text-lg"
              value={workflowName}
              onChange={(e) => {
                setWorkflowName(e.target.value);
                document
                  .getElementById("workflowName")
                  ?.classList.remove("input-error");
              }}
            />
            {workflowId && (
              <span className="badge badge-neutral">Editing existing workflow</span>
            )}
          </div>

          <section className="flex-1">
            <WorkflowCanvas
              workflowItems={workflowItems}
              setWorkflowItems={setWorkflowItems}
              onCompile={compileWorkflow}
            />
          </section>
        </div>

        {/* Right: Logs */}
        <LogsPanel output={output} />
      </div>
    </div>
  );
}
