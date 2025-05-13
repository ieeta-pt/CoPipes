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
            document.getElementById("workflowName")?.classList.remove("input-error");
          }}
        />
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
