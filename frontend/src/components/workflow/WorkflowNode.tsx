"use client";

import { Handle, Position, NodeProps } from "reactflow";
import { X, GripVertical } from "lucide-react";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { Registry } from "@/components/airflow-tasks/Registry";

type WorkflowNodeData = {
  item: WorkflowComponent;
  onRemove: (id: string) => void;
  onUpdate: (config: WorkflowComponent["config"]) => void;
};

export function WorkflowNode({ data }: NodeProps<WorkflowNodeData>) {
  const { item, onRemove, onUpdate } = data;
  const TaskComponent = Registry[item.content]?.component;

  return (
    <div
      className="card bg-base-100 shadow-md"
      style={{
        borderLeft: `4px solid ${getColorForType(item.type)}`,
        minWidth: "10px",
      }}
    >
      <Handle type="target" position={Position.Top} className="w-3 h-3" />

      <div className="card-body w-full p-4">
        <div className="flex justify-between items-start mb-2">
          <div className="text-lg font-semibold">{item.content}</div>
          <div className="flex gap-2">
            <button
              className="btn btn-xs btn-error btn-soft"
              onClick={() => onRemove(item.id)}
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>
        {TaskComponent && (
          <TaskComponent config={item.config} onUpdate={onUpdate} />
        )}
      </div>

      <Handle type="source" position={Position.Bottom} className="w-3 h-3" />
    </div>
  );
}

WorkflowNode.displayName = "WorkflowNode";

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
