"use client";
import WorkflowEditor from "@/components/workflow/WorkflowEditor";
import { useParams } from "next/navigation";

export default function WorkflowEditorPage() {
  const params = useParams();
  const workflowId = params.id?.[0];

  return (
    <main className="min-h-screen">
      <WorkflowEditor workflowId={workflowId} />
    </main>
  );
}
