// components/workflow-table-wrapper.tsx
"use client";

import { useEffect, useState } from "react";
import { getWorkflows } from "@/api/dashboard/table";
import { Workflow, columns } from "@/app/dashboard/columns";
import { DataTable } from "@/components/dashboard/DataTable";

export function WorkflowTableWrapper() {
  const [data, setData] = useState<Workflow[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    setIsLoading(true);
    getWorkflows()
      .then(setData)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading loading-spinner loading-lg text-primary"></div>
      </div>
    );
  }

  return <DataTable columns={columns} data={data} />;
}
