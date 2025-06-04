"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Download, Pencil, Play, Trash, Copy } from "lucide-react";
import { deleteWorkflowAPI, downloadWorkflowAPI, copyWorkflowAPI } from "@/api/workflows";
import AvatarStack from "@/components/workflow/AvatarStack";
export type Workflow = {
  id: number;
  name: string;
  last_edit: string;
  last_run: string | null;
  status: "success" | "failed" | "queued" | "draft" | "running";
  collaborators: string[];
  user_id: string;
  owner_email?: string; // Owner's email
  owner_name?: string;  // Owner's display name
  created_at: string;
  role?: "owner" | "collaborator";
  organization_id?: string | null; // Organization ID if workflow belongs to org
  organization_name?: string; // Organization name for display
  permissions?: {
    is_owner: boolean;
    can_edit: boolean;
    can_execute: boolean;
    can_download: boolean;
    can_delete: boolean;
    can_copy: boolean;
    can_manage_collaborators: boolean;
  };
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

const copyWorkflow = async (name: string) => {
  try {
    const result = await copyWorkflowAPI(name);
    
    // Show success message and optionally redirect to the new workflow
    if (result.new_workflow_name) {
      const newWorkflowName = result.new_workflow_name.replace(/ /g, "_");
      
      // Ask user if they want to edit the copied workflow
      const shouldEdit = confirm(`Workflow copied successfully as "${result.new_workflow_name}". Would you like to edit the copy now?`);
      
      if (shouldEdit) {
        window.location.href = `/workflow/editor/${newWorkflowName}`;
      } else {
        // Just reload the page to show the new workflow in the list
        window.location.reload();
      }
    } else {
      alert("Workflow copied successfully!");
      window.location.reload();
    }
  } catch (error) {
    console.error("Error copying workflow:", error);
    const errorMessage = error instanceof Error ? error.message : "Failed to copy workflow";
    alert(`Error copying workflow: ${errorMessage}`);
  }
};

export const columns: ColumnDef<Workflow>[] = [
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "owner_email",
    header: "Owner",
    cell: ({ row }) => {
      const workflow = row.original;
      const ownerEmail = workflow.owner_email;
      const ownerName = workflow.owner_name;
      const isCurrentUserOwner = workflow.role === "owner";
      
      // Display owner information
      const displayName = ownerName || (ownerEmail ? ownerEmail.split('@')[0] : 'Unknown');
      const displayText = isCurrentUserOwner ? "You" : displayName;
      
      return (
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-blue-400 flex items-center justify-center text-white text-xs font-medium">
            {isCurrentUserOwner ? "Y" : displayName.charAt(0).toUpperCase()}
          </div>
          <span className={`text-sm ${isCurrentUserOwner ? "font-medium" : ""}`}>
            {displayText}
          </span>
        </div>
      );
    },
  },
  {
    accessorKey: "organization_name",
    header: "Organization",
    cell: ({ row }) => {
      const workflow = row.original;
      const orgName = workflow.organization_name;
      
      if (!orgName) {
        return (
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-gray-400 flex items-center justify-center text-white text-xs font-medium">
              P
            </div>
            <span className="text-sm text-base-content/70">Personal</span>
          </div>
        );
      }
      
      return (
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-full bg-purple-500 flex items-center justify-center text-white text-xs font-medium">
            {orgName.charAt(0).toUpperCase()}
          </div>
          <span className="text-sm font-medium">{orgName}</span>
        </div>
      );
    },
  },
  {
    accessorKey: "collaborators",
    header: "Collaborators",
    cell: ({ row }) => {
      const collaborators = row.getValue("collaborators") as string[] | null;
      const collabArray = Array.isArray(collaborators) ? collaborators : [];
      
      return (
        <AvatarStack 
          collaborators={collabArray} 
          maxVisible={3} 
          size="sm" 
        />
      );
    },
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
  
  {
    id: "actions",
    cell: ({ row }) => {
      const workflow = row.original;
      const permissions = workflow.permissions;

      return (
        <div className="flex justify-end gap-2">
          {(!permissions || permissions.can_edit) && (
            <button
              className="btn btn-soft btn-accent btn-xs"
              onClick={() => editWorkflow(workflow.name)}
              title="Edit workflow"
            >
              <Pencil className="h4 w-4" />
            </button>
          )}

          {(!permissions || permissions.can_execute) && (
            <button
              className="btn btn-soft btn-primary btn-xs"
              onClick={() => runWorkflow(workflow.name)}
              title="Execute workflow"
            >
              <Play className="h-4 w-4" />
            </button>
          )}

          {(!permissions || permissions.can_copy) && (
            <button
              className="btn btn-soft btn-info btn-xs"
              onClick={() => copyWorkflow(workflow.name)}
              title="Copy workflow"
            >
              <Copy className="h-4 w-4" />
            </button>
          )}

          {(!permissions || permissions.can_download) && (
            <button
              className="btn btn-soft btn-secondary btn-xs"
              onClick={() => downloadWorkflow(workflow.name)}
              title="Download workflow"
            >
              <Download className="h-4 w-4" />
            </button>
          )}

          {(!permissions || permissions.can_delete) && (
            <button
              className="btn btn-soft btn-error btn-xs"
              onClick={() => deleteWorkflow(workflow.name)}
              title="Delete workflow"
            >
              <Trash className="h-4 w-4" />
            </button>
          )}
        </div>
      );
    },
  },
];
