"use client";

import { TaskInstance } from "@/components/workflow/history/types";

interface TaskResultsProps {
  taskInstances: TaskInstance[];
}

export function TaskResults({ taskInstances }: TaskResultsProps) {
  const getStateColor = (state: string) => {
    switch (state) {
      case "success":
        return "text-green-600 bg-green-100";
      case "failed":
        return "text-red-600 bg-red-100";
      case "running":
        return "text-blue-600 bg-blue-100";
      case "queued":
        return "text-yellow-600 bg-yellow-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  return (
    <div className="border border-base-300 rounded-lg p-4">
      <h3 className="font-semibold mb-3">Task Results</h3>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {taskInstances.map((task) => (
          <div key={task.task_id} className="border border-base-200 rounded p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">{task.task_id}</span>
              <span
                className={`px-2 py-1 rounded-full text-xs font-medium ${getStateColor(
                  task.state
                )}`}
              >
                {task.state}
              </span>
            </div>
            
            {task.duration && (
              <div className="text-sm text-base-content/70 mb-2">
                Duration: {task.duration.toFixed(2)}s
              </div>
            )}

            {/* XCOM Data */}
            {task.xcom_entries && task.xcom_entries.length > 0 && (
              <div className="mt-3">
                <h4 className="text-sm font-medium mb-2">Output Data:</h4>
                <div className="space-y-2">
                  {task.xcom_entries.map((xcom, idx) => (
                    <div key={idx} className="bg-base-50 p-2 rounded text-xs">
                      <div className="font-medium">{xcom.key}:</div>
                      <pre className="mt-1 whitespace-pre-wrap max-h-32 overflow-y-auto">
                        {typeof xcom.value === "object"
                          ? JSON.stringify(xcom.value, null, 2)
                          : String(xcom.value)}
                      </pre>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}