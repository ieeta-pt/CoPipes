"use client";

import { RunSummary } from "@/components/workflow/history/RunSummary";
import { TaskResults } from "@/components/workflow/history/TaskResults";
import { RunDetailsData } from "@/components/workflow/history/types";

interface RunDetailsProps {
  selectedRun: RunDetailsData | null;
}

export function RunDetails({ selectedRun }: RunDetailsProps) {
  return (
    <div className="card bg-base-100 shadow-xl">
      <div className="card-body">
        <h2 className="card-title">Run Details</h2>
        
        {!selectedRun ? (
          <div className="text-center py-8 text-base-content/60">
            Select a run to view details
          </div>
        ) : (
          <div className="space-y-6">
            <RunSummary dagRun={selectedRun.dag_run} />
            <TaskResults taskInstances={selectedRun.task_instances} />
          </div>
        )}
      </div>
    </div>
  );
}