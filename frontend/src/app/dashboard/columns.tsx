"use client";

import { ColumnDef } from "@tanstack/react-table";
import { Pencil, Play, Trash } from "lucide-react";

export type Workflow = {
  id: string;
  name: string;
  last_edit: string;
  last_run: string;
  last_run_status: "Success" | "Failed" | "Running";
  people: string[];
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
      const date = new Date(row.getValue("last_run"));
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    },
  },
  {
    accessorKey: "last_run_status",
    header: "Last Run Status",
    cell: ({ row }) => {
      const status = row.getValue("last_run_status") as
        | "Success"
        | "Failed"
        | "Running";
      return (
        <span
          className={`badge badge-soft ${
            status === "Success"
              ? " badge-success"
              : status === "Failed"
              ? "badge-error"
              : "badge-warning"
          }`}
        >
          {status}
        </span>
      );
    },
  },
  {
    accessorKey: "people",
    header: "People",
  },
  {
    id: "actions",
    cell: ({ row }) => {
      const workflow = row.original;

      return (
        <div className="flex justify-end gap-2">
          <button
            className="btn btn-soft btn-secondary btn-xs"
            onClick={() => console.log("Open in editor")}
          >
            <Pencil className="h4 w-4" />
          </button>

          <button
            className="btn btn-soft btn-primary btn-xs"
            onClick={() => console.log("Test")}
          >
            <Play className="h-4 w-4" />
          </button>

          <button
            className="btn btn-soft btn-error btn-xs"
            onClick={() => console.log("Delete")}
          >
            <Trash className="h-4 w-4" />
          </button>

        </div>
      );
    },
  },
];
