"use client";
import WorkflowEditor from "@/components/workflow/editor/WorkflowEditor";
import { useParams } from "next/navigation";
import { withAuth } from "@/contexts/AuthContext";

function WorkflowEditorPage() {
  const params = useParams() as { id?: string[] };
  const workflowId = params.id?.[0];

  return (
    <main className="min-h-screen">
      <WorkflowEditor workflowId={workflowId} />
    </main>
  );
}

export default withAuth(WorkflowEditorPage);
