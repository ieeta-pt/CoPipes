// components/workflow-table-wrapper.tsx
"use client";

import { useEffect, useState, useRef } from "react";
import { getWorkflows, uploadWorkflowAPI } from "@/api/dashboard/table";
import { Workflow, columns } from "@/app/dashboard/columns";
import { DataTable } from "@/components/dashboard/DataTable";
import { Upload } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";

export function WorkflowTableWrapper() {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [data, setData] = useState<Workflow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Don't fetch if still loading auth or not authenticated
    if (authLoading || !isAuthenticated) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    getWorkflows()
      .then(setData)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, [authLoading, isAuthenticated]);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.json')) {
      alert('Please select a JSON file');
      return;
    }

    try {
      // Read file content to validate JSON
      const text = await file.text();
      const workflowData = JSON.parse(text);
      
      // Validate that it has the expected structure
      if (!workflowData.dag_id || !workflowData.tasks) {
        alert('Invalid workflow file format. Missing dag_id or tasks.');
        return;
      }

      // Upload the workflow
      const result = await uploadWorkflowAPI(file);
      
      // Redirect to editor with the uploaded workflow
      window.location.href = `/workflow/editor/${result.dag_id}`;
      
    } catch (error) {
      console.error('Error uploading workflow:', error);
      alert('Error uploading workflow. Please check the file format.');
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="loading loading-spinner loading-lg text-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex flex-col">
      <div className="flex justify-end gap-2 m-4">
      <a href="/workflow/editor" className="btn btn-soft btn-primary">
          Create workflow
        </a>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileUpload}
          className="hidden"
        />
        <button
          onClick={handleUploadClick}
          className="btn btn-soft btn-secondary"
        >
          <Upload className="h-4 w-4 mr-2" />
          Upload workflow
        </button>
      </div>
      <DataTable columns={columns} data={data} />
    </div>
  );
}
