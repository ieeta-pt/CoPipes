// components/workflow-table-wrapper.tsx
"use client";

import { useEffect, useState } from "react";
import { getWorkflows } from "@/api/dashboard/table";
import { Workflow, columns } from "@/app/dashboard/columns";
import { DataTable } from "@/app/dashboard/data-table";

export function WorkflowTableWrapper() {
  const [data, setData] = useState<Workflow[]>([]);

  useEffect(() => {
    getWorkflows().then(setData).catch(console.error);
  }, []);

  console.log("Workflow data:", data);

  return <DataTable columns={columns} data={data} />;
}
