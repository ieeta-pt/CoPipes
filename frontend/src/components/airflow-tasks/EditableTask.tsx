import React from "react";
import { TaskConfig, WorkflowComponent } from "@/components/airflow-tasks/types";
import { ValidatedTask } from "@/components/airflow-tasks/ValidatedTask";

interface EditableTaskProps {
  config: TaskConfig;
  onUpdate: (newConfig: TaskConfig) => void;
  availableTasks?: WorkflowComponent[];
  taskId?: string;
}

export const EditableTask: React.FC<EditableTaskProps> = ({
  config,
  onUpdate,
  availableTasks,
  taskId,
}) => {
  return (
    <ValidatedTask
      config={config}
      onUpdate={onUpdate}
      availableTasks={availableTasks}
      taskId={taskId}
    />
  );
};