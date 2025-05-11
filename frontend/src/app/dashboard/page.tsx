import { WorkflowTableWrapper } from "@/components/dashboard/workflow-table-wrapper";

export default async function TablePage() {
  return (
    <div className="container mx-auto py-10">
      <WorkflowTableWrapper />
      <div className="flex justify-center p-4">
        <a href="/workflow/editor" className="btn btn-soft btn-wide btn-primary">
          + Add New Workflow
        </a>
      </div>
    </div>
  );
}
