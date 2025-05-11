"use client";

import { useState } from "react";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { Registry } from "@/components/airflow-tasks/Registry";
import { Sidebar } from "@/components/workflow/Sidebar";
import { LogsPanel } from "@/components/workflow/LogsPanel";
import { WorkflowCanvas } from "./WorkflowCanvas";
import { submitWorkflow } from "@/api/workflow/test";

const createIdBuilder = (prefix = "id") => () =>
  `${prefix}_${Math.random().toString(36).substring(2, 4)}`;

export default function WorkflowEditor() {
  const [workflowItems, setWorkflowItems] = useState<WorkflowComponent[]>([]);
  const [output, setOutput] = useState("");
  const [workflowName, setWorkflowName] = useState("");
  const [isOpen, setIsOpen] = useState(true);

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

    const payload = {
      dag_id: workflowName,
      tasks: workflowItems,
    };

    try {
      const result = await submitWorkflow(payload);
      setOutput(JSON.stringify(result, null, 2));
    } catch (err) {
      console.error(err);
      setOutput("❌ Failed to compile workflow");
    }
  };

  return (
    <div className="flex h-[calc(100%-2rem)]">
      {/* Sidebar stays unchanged */}
      <Sidebar onAddComponent={addComponent} />
  
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="p-2 border-base-300 bg-base-100">
          <input
            id="workflowName"
            name="workflowName"
            type="text"
            placeholder="Nameless workflow"
            className="input input-bordered w-full max-w-md text-lg"
            value={workflowName}
            onChange={(e) => {
              setWorkflowName(e.target.value);
              document.getElementById("workflowName")?.classList.remove("input-error");
            }}
          />
        </div>
  
        {/* Main canvas and logs section */}
        <div className="flex-1 flex overflow-hidden">
          <section className="flex-1 overflow-auto p-2">
            <WorkflowCanvas
              workflowItems={workflowItems}
              setWorkflowItems={setWorkflowItems}
              onCompile={compileWorkflow}
            />
          </section>
          <LogsPanel output={output} />
        </div>
      </div>
    </div>
  );
  
}
