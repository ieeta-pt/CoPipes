"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Download, Pencil, Play, Trash } from "lucide-react";
import { deleteWorkflowAPI, downloadWorkflowAPI } from "@/api/dashboard/table";
export type Workflow = {
  id: number;
  name: string;
  last_edit: string;
  last_run: string | null;
  status: "success" | "failed" | "queued" | "draft" | "running";
  collaborators: string;
  user_id: string;
  created_at: string;
};

const editWorkflow = async (name: string) => {
  try {
    name = name.replace(/ /g, "_");
    window.location.href = `/workflow/editor/${name}`;
  } catch (error) {
    console.error("Error editing workflow:", error);
  }
};

const runWorkflow = async (name: string) => {
  try {
    name = name.replace(/ /g, "_");
    window.location.href = `/workflow/execute/${name}`;
  } catch (error) {
    console.error("Error running workflow:", error);
  }
};

const deleteWorkflow = async (name: string) => {
  try {
    const response = await deleteWorkflowAPI(name);
    window.location.reload();
  } catch (error) {
    console.error("Error deleting workflow:", error);
  }
};

const downloadWorkflow = async (name: string) => {
  try {
    const workflow = await downloadWorkflowAPI(name);
    
    // Create a blob with the JSON data
    const blob = new Blob([JSON.stringify(workflow, null, 2)], {
      type: "application/json",
    });
    
    // Create a temporary download link
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${name.replace(/ /g, "_")}.json`;
    document.body.appendChild(link);
    link.click();
    
    // Clean up
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error downloading workflow:", error);
  }
};

export const columns: ColumnDef<Workflow>[] = [
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "last_edit",
    header: "Last Edit",
    cell: ({ row }) => {
      const date = new Date(row.getValue("last_edit"));
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    },
  },
  {
    accessorKey: "last_run",
    header: "Last Run",
    cell: ({ row }) => {
      const lastRun = row.getValue("last_run");
      if (!lastRun) {
        return "-";
      }
      const date = new Date(lastRun as string);
      if (isNaN(date.getTime())) {
        return "-";
      }
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    },
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }) => {
      const status = row.getValue("status") as
        | "success"
        | "failed"
        | "queued"
        | "draft"
        | "running";
      return (
        <span
          className={`badge badge-soft ${
            status === "success"
              ? "badge-success"
              : status === "failed"
              ? "badge-error"
              : status === "queued" || status === "running"
              ? "badge-warning"
              : "badge-info"
          }`}
        >
          {status.charAt(0).toUpperCase() + status.slice(1)}
        </span>
      );
    },
  },
  // {
  //   accessorKey: "owner",
  //   header: "Owner",
  // },
    // {
  //   accessorKey: "collaborators",
  //   header: "Collaborators",
  // },
  {
    id: "actions",
    cell: ({ row }) => {
      const workflow = row.original;

      return (
        <div className="flex justify-end gap-2">
          <button
            className="btn btn-soft btn-accent btn-xs"
            onClick={() => editWorkflow(workflow.name)}
          >
            <Pencil className="h4 w-4" />
          </button>

          <button
            className="btn btn-soft btn-primary btn-xs"
            onClick={() => runWorkflow(workflow.name)}
          >
            <Play className="h-4 w-4" />
          </button>

          <button
            className="btn btn-soft btn-secondary btn-xs"
            onClick={() => downloadWorkflow(workflow.name)}
          >
            <Download className="h-4 w-4" />
          </button>

          <button
            className="btn btn-soft btn-error btn-xs"
            onClick={() => deleteWorkflow(workflow.name)}
          >
            <Trash className="h-4 w-4" />
          </button>
        </div>
      );
    },
  },
];
