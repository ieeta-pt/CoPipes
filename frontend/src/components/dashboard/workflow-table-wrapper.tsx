// components/workflow-table-wrapper.tsx
"use client";

import { useEffect, useState } from "react";
import { getWorkflows } from "@/api/dashboard/table";
import { Workflow, columns } from "@/app/dashboard/columns";
import { DataTable } from "@/components/dashboard/DataTable";
import { useAuthStore } from "@/api/stores/authStore";
import { workflowsApi } from "@/api/api";

export function WorkflowTableWrapper() {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const token = useAuthStore((state) => state.token);

  useEffect(() => {
    const fetchWorkflows = async () => {
      if (!isAuthenticated || !token) return;

      try {
        setLoading(true);
        setError("");
        const data = await workflowsApi.getAll();
        setWorkflows(data);
      } catch (err) {
        console.error("Error fetching workflows:", err);
        setError("Failed to fetch workflows");
      } finally {
        setLoading(false);
      }
    };

    fetchWorkflows();
  }, [isAuthenticated, token]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return <DataTable columns={columns} data={workflows} />;
}
