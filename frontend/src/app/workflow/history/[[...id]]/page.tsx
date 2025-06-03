"use client";
import WorkflowHistory from "@/components/workflow/history/WorkflowHistory";
import { withAuth } from "@/contexts/AuthContext";

function WorkflowHistoryPage() {
  return (
    <main className="min-h-screen">
      <WorkflowHistory />
    </main>
  );
}

export default withAuth(WorkflowHistoryPage);