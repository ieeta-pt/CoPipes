"use client";
import WorkflowExecute from "@/components/workflow/execute/WorkflowExecute";
import { useParams } from "next/navigation";
import { withAuth } from "@/contexts/AuthContext";

function WorkflowExecutePage() {
  const params = useParams() as { id?: string[] };
  const workflowId = params.id?.[0];

  return (
    <main className="min-h-screen">
      <WorkflowExecute workflowId={workflowId} />
    </main>
  );
}

export default withAuth(WorkflowExecutePage);
