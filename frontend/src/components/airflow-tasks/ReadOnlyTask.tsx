import React from "react";
import { TaskConfig } from "@/components/airflow-tasks/types";

interface ReadOnlyTaskProps {
  config: TaskConfig;
}

export const ReadOnlyTask: React.FC<ReadOnlyTaskProps> = ({ config }) => {
  return (
    <div className="space-y-3">
      {config.map((field) => (
        <div key={field.name} className="flex flex-col">
          <span className="text-sm font-medium text-gray-700 mb-1">
            {field.name}
          </span>
          <div className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-md text-sm text-gray-600">
            {field.placeholder || `Enter ${field.name.toLowerCase()}`}
          </div>
        </div>
      ))}
    </div>
  );
};