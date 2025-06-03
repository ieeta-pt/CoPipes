"use client";

import { WorkflowRun } from "@/components/workflow/history/types";

interface RunSummaryProps {
  dagRun: WorkflowRun;
}

export function RunSummary({ dagRun }: RunSummaryProps) {
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (start: string, end: string | null) => {
    if (!end) return "N/A";
    const startTime = new Date(start).getTime();
    const endTime = new Date(end).getTime();
    const duration = (endTime - startTime) / 1000;
    return `${duration.toFixed(1)}s`;
  };

  return (
    <div className="border border-base-300 rounded-lg p-4">
      <h3 className="font-semibold mb-3">Run Summary</h3>
      <div className="grid grid-cols-1 gap-2 text-sm">
        <div className="flex justify-between">
          <span>Run ID:</span>
          <span className="font-mono">{dagRun.dag_run_id}</span>
        </div>
        <div className="flex justify-between">
          <span>Status:</span>
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${getStateColor(
              dagRun.state
            )}`}
          >
            {dagRun.state}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Started:</span>
          <span>{formatDate(dagRun.start_date)}</span>
        </div>
        {dagRun.end_date && (
          <div className="flex justify-between">
            <span>Finished:</span>
            <span>{formatDate(dagRun.end_date)}</span>
          </div>
        )}
        <div className="flex justify-between">
          <span>Duration:</span>
          <span>
            {formatDuration(dagRun.start_date, dagRun.end_date)}
          </span>
        </div>
        <div className="flex justify-between">
          <span>Run Type:</span>
          <span className="capitalize">{dagRun.run_type}</span>
        </div>
        <div className="flex justify-between">
          <span>External Trigger:</span>
          <span>{dagRun.external_trigger ? "Yes" : "No"}</span>
        </div>
      </div>
    </div>
  );
}