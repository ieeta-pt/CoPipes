"use client";
import WorkflowEditor from "@/components/workflow/editor/WorkflowEditor";
import { useParams } from "next/navigation";

export default function WorkflowEditorPage() {
  const params = useParams() as { id?: string[] };
  const workflowId = params.id?.[0];

  return (
    <main className="min-h-screen">
        <h1>Downloading workflow {workflowId}</h1>
    </main>
  );
}