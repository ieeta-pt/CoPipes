"use client";

import { WorkflowTableWrapper } from "@/components/dashboard/workflow-table-wrapper";
import { withAuth } from "@/contexts/AuthContext";

function TablePage() {
  return (
    <div className="container mx-auto">
      <WorkflowTableWrapper />
    </div>
  );
}

export default withAuth(TablePage);
