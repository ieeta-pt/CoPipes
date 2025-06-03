"use client";

import { Calendar, Clock, User, Eye } from "lucide-react";
import { WorkflowRun } from "@/components/workflow/history/types";

interface RunsListProps {
  runs: WorkflowRun[];
  onRunSelect: (dagRunId: string) => void;
}

export function RunsList({ runs, onRunSelect }: RunsListProps) {
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
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title flex items-center gap-2">
          <Calendar className="w-5 h-5" />
          Recent Runs
        </h2>
        
        {runs.length === 0 ? (
          <div className="text-center py-8 text-base-content/60">
            No runs found for this workflow
          </div>
        ) : (
          <div className="space-y-4">
            {runs.map((run) => (
              <div
                key={run.dag_run_id}
                className="border border-base-300 rounded-lg p-4 hover:bg-base-50 cursor-pointer transition-colors"
                onClick={() => onRunSelect(run.dag_run_id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${getStateColor(
                        run.state
                      )}`}
                    >
                      {run.state}
                    </span>
                    <span className="font-mono text-sm">
                      {run.dag_run_id}
                    </span>
                  </div>
                  <Eye className="w-4 h-4 text-base-content/60" />
                </div>
                
                <div className="mt-3 grid grid-cols-2 gap-4 text-sm text-base-content/70">
                  <div className="flex items-center gap-2">
                    <Clock className="w-4 h-4" />
                    <span>Started: {formatDate(run.start_date)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    <span>Type: {run.run_type}</span>
                  </div>
                </div>
                
                {run.end_date && (
                  <div className="mt-2 text-sm text-base-content/70">
                    Duration: {formatDuration(run.start_date, run.end_date)}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}