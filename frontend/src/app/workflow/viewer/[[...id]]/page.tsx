"use client";

import { use } from "react";
import { withAuth } from "@/contexts/AuthContext";
import WorkflowViewer from "@/components/workflow/viewer/WorkflowViewer";

function WorkflowViewerPage({ params }: { params: Promise<{ id?: string[] }> }) {
  const resolvedParams = use(params);
  const workflowId = resolvedParams.id?.[0];

  if (!workflowId) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="alert alert-warning max-w-lg">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="stroke-current shrink-0 h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z"
            />
          </svg>
          <span>No workflow ID provided</span>
        </div>
      </div>
    );
  }

  return <WorkflowViewer workflowId={workflowId} />;
}

export default withAuth(WorkflowViewerPage);