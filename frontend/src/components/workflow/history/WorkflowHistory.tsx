"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { RunsList } from "@/components/workflow/history/RunsList";
import { RunDetails } from "@/components/workflow/history/RunDetails";
import { showToast } from "@/components/layout/ShowToast";
import { WorkflowRun, RunDetailsData } from "@/components/workflow/history/types";
import { apiClient } from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";

export default function WorkflowHistory()  {
  const params = useParams() as {id?: string[]};
  const workflowName = params.id?.[0] as string || '';
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [runs, setRuns] = useState<WorkflowRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<RunDetailsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (workflowName && isAuthenticated && !authLoading) {
      fetchWorkflowRuns();
    }
  }, [workflowName, isAuthenticated, authLoading]);

  const fetchWorkflowRuns = async () => {
    try {
      const data = await apiClient.get(`/api/workflows/${workflowName}/runs`);
      setRuns(data.runs || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "An error occurred";
      setError(errorMessage);
      showToast("Failed to load workflow history", "error");
    } finally {
      setLoading(false);
    }
  };

  const fetchRunDetails = async (dagRunId: string) => {
    try {
      const data = await apiClient.get(`/api/workflows/${workflowName}/runs/${dagRunId}`);
      setSelectedRun(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to fetch run details";
      setError(errorMessage);
      showToast("Failed to load run details", "error");
    }
  };

  if (loading || authLoading) {
    return (
      <div className="min-h-screen bg-base-200 p-8">
        <div className="flex items-center justify-center">
          <span className="loading loading-spinner loading-lg"></span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-base-200 p-8">
        <div className="alert alert-error">
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-base-200 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center gap-4 mb-8">
         <Link href={`/workflow/execute/${workflowName}`} className="btn btn-ghost btn-sm">
            <ChevronLeft className="w-4 h-4" />
            Back
          </Link>
          <h1 className="text-3xl font-bold">
            Execution history: {workflowName.replace(/_/g, " ")}
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <RunsList
            runs={runs}
            onRunSelect={fetchRunDetails}
          />
          <RunDetails
            selectedRun={selectedRun}
          />
        </div>
      </div>
    </div>
  );
}