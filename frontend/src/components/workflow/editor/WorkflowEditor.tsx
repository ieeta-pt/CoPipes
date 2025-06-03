"use client";

import { useState, useEffect, useRef } from "react";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { Registry } from "@/components/airflow-tasks/Registry";
import { Sidebar } from "@/components/workflow/Sidebar";
import { WorkflowCanvas } from "@/components/workflow/WorkflowCanvas";
import CollaboratorManager from "@/components/workflow/CollaboratorManager";
import PresenceIndicator, {
  ActivityFeed,
} from "@/components/workflow/PresenceIndicator";
import { useRealtimeCollaboration } from "@/hooks/useRealtimeCollaboration";
import { CursorOverlay } from "@/components/workflow/RealtimeCursor";
import {
  submitWorkflow,
  getWorkflow,
  updateWorkflow,
} from "@/api/workflow/test";
import { useRouter } from "next/navigation";
import { Settings, Users, Activity } from "lucide-react";
import { showToast } from "@/components/layout/ShowToast";
import { useAuth } from "@/contexts/AuthContext";

const createIdBuilder =
  (prefix = "id") =>
  () =>
    `${prefix}_${Math.random().toString(36).substring(2, 5)}`;

export default function WorkflowEditor({
  workflowId,
}: {
  workflowId?: string;
}) {
  const { isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();
  const [workflowItems, setWorkflowItems] = useState<WorkflowComponent[]>([]);
  const [workflowName, setWorkflowName] = useState("");
  const [isLoading, setIsLoading] = useState(!!workflowId);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [collaborators, setCollaborators] = useState<string[]>([]);
  const [permissions, setPermissions] = useState<any>(null);
  const [showCollaborators, setShowCollaborators] = useState(false);
  const [showActivity, setShowActivity] = useState(false);
  const fetchingRef = useRef(false);

  // Realtime collaboration - temporarily using debug version

  const { otherUsers, updateCursor } = useRealtimeCollaboration(workflowId);

  // Track mouse movement for real-time cursors
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      // Always track cursor position so other users can see it
      if (updateCursor) {
        updateCursor(e.clientX, e.clientY);
      }
    };

    // Only add listener if we have a workflowId
    if (workflowId) {
      window.addEventListener("mousemove", handleMouseMove);
    }

    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, [updateCursor, workflowId]);

  useEffect(() => {
    async function fetchWorkflow() {
      // Prevent duplicate calls
      if (fetchingRef.current) {
        return;
      }

      // Don't fetch if still loading auth or not authenticated
      if (authLoading || !isAuthenticated) {
        return;
      }

      if (workflowId) {
        fetchingRef.current = true;
        try {
          setIsLoading(true);
          setError(null);
          console.log("Fetching workflow:", workflowId);
          const workflow = await getWorkflow(workflowId);
          setWorkflowName(workflow.dag_id.replace(/_/g, " "));
          console.log("Fetched workflow:", workflow.dag_id);
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

          // Set collaboration data - ensure collaborators is always an array
          setCollaborators(
            Array.isArray(workflow.collaborators) ? workflow.collaborators : []
          );
          setPermissions(workflow.permissions || null);
        } catch (error) {
          setError(
            "Failed to fetch workflow. It might have been deleted or you don't have permission to view it."
          );
          console.error(error);
        } finally {
          setIsLoading(false);
          setIsEditing(true);
          fetchingRef.current = false;
        }
      }
    }

    fetchWorkflow();
  }, [workflowId, authLoading, isAuthenticated]);

  const addComponent = (content: string) => {
    const taskDef = Registry[content];
    const newItem: WorkflowComponent = {
      id: createIdBuilder(content)(),
      content,
      type: taskDef.type,
      subtype: taskDef.subtype,
      config: [...taskDef.defaultConfig],
    };
    setWorkflowItems([...workflowItems, newItem]);
  };

  const compileWorkflow = async () => {
    // Scroll to top of the page
    window.scrollTo({ top: 0, behavior: "smooth" });

    if (!workflowName) {
      showToast("Workflow name is required.", "warning");
      document.getElementById("workflowName")?.classList.add("input-error");
      return;
    }

    console.log("Compiling workflow with items:", workflowItems);

    const validatedItems = workflowItems.map((item) => ({
      id: item.id,
      content: item.content,
      type: item.type,
      subtype: item.subtype || "",
      config: item.config.map((conf) => {
        const configField: any = {
          name: conf.name,
          value: conf.value || "",
          type:
            conf.type === "task_reference" ? "string" : conf.type || "string",
        };

        // Only include options if they exist and are not empty
        if (conf.options && conf.options.length > 0) {
          configField.options = conf.options;
        }

        return configField;
      }),
      dependencies: item.dependencies || [],
    }));

    const payload = {
      dag_id: workflowName,
      tasks: validatedItems,
    };

    try {
      showToast("Compiling workflow...", "info");
      if (isEditing) {
        setResult(await updateWorkflow(payload.dag_id, payload));
      } else {
        setResult(await submitWorkflow(payload));
      }
      showToast("Workflow compiled successfully.", "success");
    } catch (err) {
      console.error(err);
      showToast("Failed to compile workflow.", "error");
    }
  };

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
      {/* Sidebar stays outside this block */}
      <Sidebar onAddComponent={addComponent} />

      <div className="flex flex-1 gap-4">
        {/* Left: Input + Canvas */}
        <div className="flex flex-col flex-1 gap-4">
          <div className="flex justify-between">
            <div className="flex items-center gap-2">
              <input
                id="workflowName"
                name="workflowName"
                type="text"
                placeholder="Nameless workflow"
                className="input input-bordered w-full max-w-md text-lg"
                value={workflowName}
                onChange={(e) => {
                  if (!isEditing) {
                    document
                      .getElementById("workflowName")
                      ?.classList.remove("input-error");
                    const regex = /^[a-zA-Z0-9\s]*$/;
                    if (!regex.test(e.target.value)) {
                      showToast(
                        "Workflow name can only contain letters, numbers and white spaces.",
                        "warning"
                      );
                      document
                        .getElementById("workflowName")
                        ?.classList.add("input-error");
                    } else {
                      setWorkflowName(e.target.value);
                    }
                  }
                }}
                readOnly={isEditing}
              />
              <button
                disabled={
                  workflowItems.length === 0 ||
                  (permissions && !permissions.can_edit)
                }
                className="btn btn-primary text-white"
                onClick={compileWorkflow}
              >
                <Settings className="h-4 w-4 mr-2" /> Compile
              </button>
            </div>

            <div className="flex items-center gap-2">
              {/* Realtime presence indicator */}
              {workflowId && (
                <PresenceIndicator workflowId={workflowId} className="mr-2" />
              )}

              <button
                className="btn btn-secondary"
                onClick={() => setShowCollaborators(true)}
              >
                <Users className="h-4 w-4 mr-2" />
                Collaborators ({collaborators.length})
              </button>

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
              setWorkflowItems={setWorkflowItems}
              onCompile={compileWorkflow}
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

      {/* Collaborator Management Modal */}
      {showCollaborators && (
        <div className="modal modal-open">
          <div className="modal-box max-w-2xl">
            <h3 className="font-bold text-lg mb-4">Manage Collaborators</h3>
            <CollaboratorManager
              workflowName={workflowName}
              collaborators={collaborators}
              canManageCollaborators={
                permissions?.can_manage_collaborators !== false
              } // Allow for new workflows
              onCollaboratorsChange={setCollaborators}
            />
            <div className="modal-action">
              <button
                className="btn"
                onClick={() => setShowCollaborators(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Realtime cursors - Debug version - placed at root level for proper positioning */}
      {workflowId && <CursorOverlay otherUsers={otherUsers} />}
    </div>
  );
}
