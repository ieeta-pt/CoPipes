import React from "react";
import { TaskConfig } from "@/components/airflow-tasks/types";

interface BaseTaskProps {
  config: TaskConfig;
  onUpdate: (newConfig: TaskConfig) => void;
}

export const BaseTask: React.FC<BaseTaskProps> = ({ config }) => {
  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 p-4 bg-base-100 rounded-lg min-w-0">
      {config.map((field) => (
        <div
          key={field.name}
          className="flex flex-col p-3 bg-white rounded border border-gray-200 shadow-sm"
        >
          <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">
            {field.name}
          </span>
          <span className="text-sm text-gray-900 whitespace-pre-line break-normal">
            {field.type === "file"
              ? `📎 ${field.value || "No file uploaded"}`
              : field.value || "-"}
          </span>
        </div>
      ))}
    </div>
  );
};
