import React from "react";
import { TaskConfig, WorkflowComponent } from "@/components/airflow-tasks/types";
import { ValidatedTask } from "@/components/airflow-tasks/ValidatedTask";

interface ExecutableTaskProps {
  config: TaskConfig;
  onUpdate: (newConfig: TaskConfig) => void;
  isReadOnly?: boolean;
  availableTasks?: WorkflowComponent[];
  taskId?: string;
}

export const ExecutableTask: React.FC<ExecutableTaskProps> = ({
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
