"use client";

import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useState } from "react";
import { ArrowUpDown, ChevronUp, ChevronDown, ChevronsRight, ChevronsLeft, ChevronLeft, ChevronRight } from "lucide-react";

interface DataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  showFilter?: boolean;
  globalFilter?: string;
  onGlobalFilterChange?: (value: string) => void;
}

interface DataTableFilterProps {
  globalFilter: string;
  onGlobalFilterChange: (value: string) => void;
}

export function DataTableFilter({ globalFilter, onGlobalFilterChange }: DataTableFilterProps) {
  return (
    <input
      placeholder="Filter all columns..."
      value={globalFilter}
      onChange={(event) => onGlobalFilterChange(String(event.target.value))}
      className="input input-bordered w-full max-w-sm"
    />
  );
}

export function DataTable<TData, TValue>({
  columns,
  data,
  showFilter = true,
  globalFilter: externalGlobalFilter,
  onGlobalFilterChange: externalOnGlobalFilterChange,
}: DataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [internalGlobalFilter, setInternalGlobalFilter] = useState("");
  
  const globalFilter = externalGlobalFilter !== undefined ? externalGlobalFilter : internalGlobalFilter;
  const setGlobalFilter = externalOnGlobalFilterChange || setInternalGlobalFilter;

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onGlobalFilterChange: setGlobalFilter,
    state: {
      sorting,
      columnFilters,
      globalFilter,
    },
  });

  return (
    <div className="space-y-4">
      {showFilter && (
        <div className="flex items-center space-x-2">
          <input
            placeholder="Filter all columns..."
            value={globalFilter ?? ""}
            onChange={(event) => setGlobalFilter(String(event.target.value))}
            className="input input-bordered w-full max-w-sm"
          />
        </div>
      )}

      <div className="overflow-x-auto rounded-sm bg-white shadow-sm">
        <table className="table w-full">
        {/* head */}
        <thead className="bg-base-200 text-base-content text-sm font-semibold">
          {table.getHeaderGroups().map((headerGroup) => (
            <tr key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <th key={header.id} className="px-4 py-2">
                  {header.isPlaceholder ? null : (
                    <div
                      className={header.column.getCanSort() ? "cursor-pointer select-none flex items-center gap-2" : ""}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      {flexRender(
                        header.column.columnDef.header,
                        header.getContext()
                      )}
                      {header.column.getCanSort() && (
                        <span className="ml-1">
                          {header.column.getIsSorted() === "asc" ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : header.column.getIsSorted() === "desc" ? (
                            <ChevronDown className="h-4 w-4" />
                          ) : (
                            <ArrowUpDown className="h-4 w-4" />
                          )}
                        </span>
                      )}
                    </div>
                  )}
                </th>
              ))}
            </tr>
          ))}
        </thead>

        {/* body */}
        <tbody>
          {table.getRowModel().rows?.length ? (
            table.getRowModel().rows.map((row) => (
              <tr key={row.id} data-state={row.getIsSelected() && "selected"}>
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className="text-sm px-4 py-2">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            ))
          ) : (
            <tr>
              <td
                colSpan={columns.length}
                className="h-24 text-center text-base-content/50"
              >
                No data available
              </td>
            </tr>
          )}
        </tbody>
      </table>
      </div>

      {/* Pagination */}
        <div className="flex items-center justify-end space-x-6 lg:space-x-8">
          <div className="flex items-center space-x-2">
            <p className="text-sm font-medium">Rows per page</p>
            <select
              value={table.getState().pagination.pageSize}
              onChange={(e) => {
                table.setPageSize(Number(e.target.value));
              }}
              className="select select-bordered w-20"
            >
              {[10, 20, 30, 40, 50].map((pageSize) => (
                <option key={pageSize} value={pageSize}>
                  {pageSize}
                </option>
              ))}
            </select>
          </div>
          <div className="flex w-[100px] items-center justify-center text-sm font-medium">
            Page {table.getState().pagination.pageIndex + 1} of{" "}
            {table.getPageCount() > 0 ? table.getPageCount() : 1}
          </div>
          <div className="flex items-center space-x-2">
            <button
              className="btn btn-outline btn-sm"
              onClick={() => table.setPageIndex(0)}
              disabled={!table.getCanPreviousPage()}
            >
              <ChevronsLeft className="h-4 w-4" />
            </button>
            <button
              className="btn btn-outline btn-sm"
              onClick={() => table.previousPage()}
              disabled={!table.getCanPreviousPage()}
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <button
              className="btn btn-outline btn-sm"
              onClick={() => table.nextPage()}
              disabled={!table.getCanNextPage()}
            >
              <ChevronRight className="h-4 w-4" />
            </button>
            <button
              className="btn btn-outline btn-sm"
              onClick={() => table.setPageIndex(table.getPageCount() - 1)}
              disabled={!table.getCanNextPage()}
            >
              <ChevronsRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
  );
}
