"use client";

import { useState, useEffect, useRef } from "react";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { WorkflowCanvas } from "@/components/workflow/WorkflowCanvas";
import PresenceIndicator, {
  ActivityFeed,
} from "@/components/workflow/PresenceIndicator";
import { useRealtimeCollaboration } from "@/hooks/useRealtimeCollaboration";
import { CursorOverlay } from "@/components/workflow/RealtimeCursor";
import { getWorkflow } from "@/api/workflows";
import { Activity, Users } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { WorkflowCollaborator } from "@/types/workflow";
import AvatarStack from "@/components/workflow/AvatarStack";

export default function WorkflowViewer({
  workflowId,
}: {
  workflowId: string;
}) {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const [workflowItems, setWorkflowItems] = useState<WorkflowComponent[]>([]);
  const [workflowName, setWorkflowName] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [collaborators, setCollaborators] = useState<WorkflowCollaborator[]>([]);
  const [showActivity, setShowActivity] = useState(false);
  const [selectedOrganizationName, setSelectedOrganizationName] = useState<string>("");
  const [selectedOrganization, setSelectedOrganization] = useState<string>("");
  const fetchingRef = useRef(false);

  // Realtime collaboration
  const { otherUsers, updateCursor } = useRealtimeCollaboration(workflowId);

  // Track mouse movement for real-time cursors
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (updateCursor) {
        updateCursor(e.clientX, e.clientY);
      }
    };

    if (workflowId) {
      window.addEventListener("mousemove", handleMouseMove);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, [updateCursor, workflowId]);

  useEffect(() => {
    async function fetchWorkflow() {
      if (fetchingRef.current) {
        return;
      }

      if (authLoading || !isAuthenticated) {
        return;
      }

      if (workflowId) {
        fetchingRef.current = true;
        try {
          setIsLoading(true);
          setError(null);
          const workflow = await getWorkflow(workflowId);
          setWorkflowName(workflow.dag_id.replace(/_/g, " "));
          setWorkflowItems(
            workflow.tasks.map((task: any) => ({
              ...task,
              config: task.config.map((field: any) => ({
                ...field,
                name: field.name,
                value: field.value,
                type: field.type,
              })),
            }))
          );

          setCollaborators(
            Array.isArray(workflow.collaborators) ? workflow.collaborators : []
          );
          
          if (workflow.organization_id) {
            setSelectedOrganization(workflow.organization_id);
            setSelectedOrganizationName(workflow.organization_name || "");
          }
        } catch (error) {
          setError(
            "Failed to fetch workflow. It might have been deleted or you don't have permission to view it."
          );
          console.error(error);
        } finally {
          setIsLoading(false);
          fetchingRef.current = false;
        }
      }
    }

    fetchWorkflow();
  }, [workflowId, authLoading, isAuthenticated]);

  if (authLoading || isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="loading loading-spinner loading-lg"></div>
        <span className="ml-3 text-sm text-base-content/70">
          {authLoading ? "Authenticating..." : "Loading workflow..."}
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="alert alert-error max-w-lg">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="stroke-current shrink-0 h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{error}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-1 h-[calc(100vh-4rem)] p-4 gap-4">
      <div className="flex flex-1 gap-4">
        {/* Main content */}
        <div className="flex flex-col flex-1 gap-4">
          <div className="flex justify-between">
            <div className="flex items-center gap-4">
              <div className="flex flex-col gap-2">
                <div className="text-2xl font-bold text-base-content">
                  {workflowName}
                </div>
                
                {/* Organization context indicator */}
                <div className="text-sm text-base-content/70 flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${selectedOrganization ? 'bg-purple-500' : 'bg-gray-400'}`}></div>
                  <span>
                    {selectedOrganization ? `${selectedOrganizationName || 'Organization'} workflow` : 'Personal workflow'}
                  </span>
                </div>
              </div>
              
              {/* Collaborators display */}
              {collaborators.length > 0 && (
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-base-content/70" />
                  <AvatarStack 
                    collaborators={collaborators.map(c => c.email)} 
                    maxVisible={3} 
                    size="sm" 
                  />
                  <span className="text-sm text-base-content/70">
                    {collaborators.length} collaborator{collaborators.length !== 1 ? 's' : ''}
                  </span>
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              {/* Read-only indicator */}
              <div className="badge badge-info badge-outline">
                Read Only
              </div>
              
              {/* Realtime presence indicator */}
              {workflowId && (
                <PresenceIndicator workflowId={workflowId} className="mr-2" />
              )}

              {workflowId && (
                <button
                  className="btn btn-soft btn-accent"
                  onClick={() => setShowActivity(!showActivity)}
                  title="Show live activity"
                >
                  <Activity className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>

          <section className="flex-1 relative">
            <WorkflowCanvas
              workflowItems={workflowItems}
              setWorkflowItems={() => {}} // No-op for readonly
              onCompile={() => {}} // No-op for readonly
              readOnly={true}
            />
          </section>
        </div>

        {/* Activity feed sidebar */}
        {showActivity && workflowId && (
          <div className="w-80 p-4">
            <ActivityFeed workflowId={workflowId} />
          </div>
        )}
      </div>

      {/* Realtime cursors */}
      {workflowId && <CursorOverlay otherUsers={otherUsers} />}
    </div>
  );
}