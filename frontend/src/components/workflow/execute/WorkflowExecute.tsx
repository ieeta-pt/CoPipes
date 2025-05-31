"use client";

import { useEffect, useState, useRef } from "react";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { executeWorkflow, getWorkflow, getWorkflowRunDetails } from "@/api/workflow/test";
import { Registry } from "@/components/airflow-tasks/Registry";
import { ExecutableTask } from "./ExecutableTask";
import { Play, CheckCircle, XCircle, Download, FileText } from "lucide-react";
import { ConfigSidebar } from "../ConfigSidebar";
import { ResultsSidebar } from "../ResultsSidebar";
import { showToast } from "@/components/layout/ShowToast";

function getColorForType(type: string): string {
  const colors: Record<string, string> = {
    Extraction: "#3b82f6",
    Transformation: "#10b981",
    Loading: "#f59e0b",
    Analysis: "#8b5cf6",
    General: "#6b7280",
  };
  return colors[type] || "#6b7280";
}

export default function WorkflowExecute({
  workflowId,
}: {
  workflowId?: string;
}) {
  const [workflow, setWorkflow] = useState<WorkflowComponent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState("");
  const [output, setOutput] = useState("");
  const [scheduleInfo, setScheduleInfo] = useState<{
    type: string;
    schedule_text: string;
    payload: any;
  } | null>(null);
  const modalRef = useRef<HTMLDialogElement>(null);
  
  // Execution state management
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionStatus, setExecutionStatus] = useState<'idle' | 'running' | 'success' | 'failed'>('idle');
  const [executionResult, setExecutionResult] = useState<any>(null);
  const [showResults, setShowResults] = useState(false);
  const [dagRunDetails, setDagRunDetails] = useState<any>(null);
  const [isLoadingResults, setIsLoadingResults] = useState(false);
  const moreInfoModalRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    async function fetchWorkflow() {
      if (workflowId) {
        try {
          setIsLoading(true);
          setError(null);
          showToast("Loading workflow...", "info");
          
          const workflow = await getWorkflow(workflowId);
          setWorkflowName(workflow.dag_id.replace(/_/g, " "));
          console.log("Fetched workflow:", workflow.dag_id);
          setWorkflow(
            workflow.tasks.map((task: any) => {
              // Get original config from Registry to restore field types
              const registryEntry = Registry[task.content];
              const originalConfig = registryEntry?.defaultConfig || [];

              return {
                ...task,
                config: task.config.map((field: any) => {
                  // Find the original field definition to get the correct type
                  const originalField = originalConfig.find(
                    (f) => f.name === field.name
                  );
                  return {
                    ...field,
                    name: field.name,
                    value: field.value,
                    type: originalField?.type || field.type, // Use original type if available
                    placeholder: originalField?.placeholder,
                    required: originalField?.required,
                    validation: originalField?.validation,
                    options: originalField?.options,
                  };
                }),
              };
            })
          );
          showToast("Workflow loaded successfully!", "success");
        } catch (error) {
          const errorMessage = "Failed to fetch workflow. It might have been deleted or you don't have permission to view it.";
          setError(errorMessage);
          showToast(errorMessage, "error");
          console.error(error);
        } finally {
          setIsLoading(false);
        }
      }
    }
    fetchWorkflow();
  }, [workflowId]);

  function getScheduleFromSidebar() {
    const configSidebar = document.querySelector("[data-schedule-type]");
    if (!configSidebar) return null;

    const type = configSidebar.getAttribute("data-schedule-type") || "now";
    console.log("Schedule type from sidebar:", type);

    let schedule_text = "";
    let payload: any = {};

    switch (type) {
      case "now":
        schedule_text = "Execute immediately";
        // no payload because we want start_date and schedule to be set to None in the DAG
        break;
      case "later":
        const dateInput = document.querySelector(
          'input[type="date"]'
        ) as HTMLInputElement;
        const date = dateInput?.value || new Date().toISOString();
        schedule_text = `Execute on ${date}`;
        payload = {
          schedule: "@once",
          start_date: date,
        };
        break;
      case "multiple":
        // Get the cron expression from the CronBuilder component
        const cronContainer = document.querySelector("[data-schedule-type='multiple']");
        const cronLink = cronContainer?.querySelector("a[href*='crontab.guru']");
        let cronExpression = "* * * * *"; // default
        
        if (cronLink) {
          const href = cronLink.getAttribute("href");
          const match = href?.match(/#(.+)$/);
          if (match) {
            cronExpression = match[1].replace(/_/g, " ");
          }
        }
        
        console.log("Extracted cron expression:", cronExpression);
        schedule_text = `Execute: ${cronExpression}`;
        payload = {
          schedule: cronExpression,
          start_date: new Date().toISOString().split("T")[0] 
        };
        break;
      default:
        schedule_text = "Execute immediately";
        // no payload because we want start_date and schedule to be set to None in the DAG
    }

    return { type, schedule_text, payload };
  }

  function handleExecuteClick() {
    const scheduleData = getScheduleFromSidebar();
    if (scheduleData) {
      setScheduleInfo(scheduleData);
      modalRef.current?.showModal();
    }
  }

  function handleConfirmExecution() {
    modalRef.current?.close();
    if (scheduleInfo) {
      runWorkflow(scheduleInfo.payload);
    }
  }

  function handleCancelExecution() {
    modalRef.current?.close();
    setScheduleInfo(null);
  }

  function validateWorkflow(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    workflow.forEach((task, taskIndex) => {
      task.config.forEach((field) => {
        if (field.required && !field.value) {
          errors.push(
            `Task ${taskIndex + 1} (${task.content}): ${field.name} is required`
          );
        }

        if (field.validation?.pattern && field.value) {
          const regex = new RegExp(field.validation.pattern);
          if (!regex.test(field.value)) {
            errors.push(
              `Task ${taskIndex + 1} (${task.content}): ${
                field.validation.message || `Invalid format for ${field.name}`
              }`
            );
          }
        }
      });
    });

    return { isValid: errors.length === 0, errors };
  }

  async function runWorkflow(schedulePayload?: any) {
    if (!workflowId) return;

    const validation = validateWorkflow();
    if (!validation.isValid) {
      const errorMessage = `Validation errors:\n${validation.errors.join("\n")}`;
      setOutput(errorMessage);
      showToast("Workflow validation failed. Please check the configuration.", "error");
      return;
    }

    try {
      setIsExecuting(true);
      setExecutionStatus('running');
      setExecutionResult(null);
      setShowResults(false);
      
      showToast("Starting workflow execution...", "info");
      
      console.log("SCHEDULE PAYLOAD: ", schedulePayload);
      const payload = {
        dag_id: workflowId.replace(/ /g, "_"),
        tasks: workflow.map((task) => ({
          id: task.id,
          type: task.type,
          content: task.content,
          subtype: task.subtype || "",
          config: task.config.map((field) => {
            const configField: any = {
              name: field.name,
              value: field.value,
              type: field.type === "task_reference" ? "string" : field.type,
            };

            // Only include options if they exist and are not empty
            if (field.options && field.options.length > 0) {
              configField.options = field.options;
            }

            return configField;
          }),
          dependencies: task.dependencies || [],
        })),
        ...schedulePayload,
      };

      console.log("Executing workflow with payload:", payload);
      const result = await executeWorkflow(workflowId, payload);
      
      setExecutionResult(result);
      setOutput(result.message || "Workflow executed successfully!");
      
      // Handle scheduled workflows (no immediate execution)
      if (result.execution_result?.status === "scheduled") {
        setExecutionStatus('success');
        showToast(result.message || "Workflow scheduled successfully!", "success");
        setShowResults(true);
        return;
      }
      
      // If we have a dag_run_id from the execution result, fetch detailed results
      if (result.execution_result?.dag_run_id) {
        showToast("Fetching execution results...", "info");
        try {
          setIsLoadingResults(true);
          const dagRunDetails = await getWorkflowRunDetails(workflowId, result.execution_result.dag_run_id);
          setDagRunDetails(dagRunDetails);
          
          // Determine final status from DAG run
          const finalStatus = dagRunDetails.dag_run?.state;
          if (finalStatus === 'success') {
            setExecutionStatus('success');
            showToast("Workflow executed successfully!", "success");
          } else if (finalStatus === 'failed') {
            setExecutionStatus('failed');
            showToast("Workflow execution failed. Check the results for details.", "error");
          } else {
            setExecutionStatus('success'); // Default to success if execution completed
            showToast("Workflow execution completed!", "success");
          }
        } catch (detailsError) {
          console.error("Failed to fetch DAG run details:", detailsError);
          setExecutionStatus('success'); // Still show success for the execution itself
          showToast("Workflow executed, but failed to fetch detailed results.", "warning");
        } finally {
          setIsLoadingResults(false);
        }
      } else {
        setExecutionStatus('success');
        showToast("Workflow executed successfully!", "success");
      }
      
      setShowResults(true);
    } catch (error) {
      console.error("Error executing workflow:", error);
      const errorMessage = "Failed to execute workflow. Please check the console for details.";
      
      setOutput(errorMessage);
      setExecutionStatus('failed');
      setExecutionResult({ error: error instanceof Error ? error.message : "Unknown error" });
      
      showToast("Workflow execution failed. Please try again.", "error");
    } finally {
      setIsExecuting(false);
    }
  }

  const handleTaskUpdate = (taskId: string, newConfig: any) => {
    setWorkflow((prevWorkflow) =>
      prevWorkflow.map((task) =>
        task.id === taskId ? { ...task, config: newConfig } : task
      )
    );
  };

  const handleViewMoreInfo = () => {
    if (!dagRunDetails) return;
    moreInfoModalRef.current?.showModal();
  };

  const handleDownloadResults = () => {
    if (!dagRunDetails) return;
    
    const dataToDownload = {
      execution_result: executionResult,
      dag_run_details: dagRunDetails,
      workflow_name: workflowName,
      timestamp: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(dataToDownload, null, 2)], {
      type: "application/json",
    });
    
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${workflowName.replace(/ /g, "_")}_execution_results_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
    
    showToast("Results downloaded successfully!", "success");
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <div className="loading loading-spinner loading-lg"></div>
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
      {/* Main content */}
      <div className="flex flex-1 gap-4">
        <div className="flex flex-col gap-4">
          <ConfigSidebar />
        </div>

        {/* Left: Input + Tasks */}
        <div className="flex flex-col flex-1 gap-4">
          <div className="flex justify-between">
            <div className="flex items-center gap-3">
              <input
                id="workflowName"
                name="workflowName"
                type="text"
                placeholder="Nameless workflow"
                className="input w-full max-w-md text-lg"
                value={workflowName}
                readOnly={true}
              />
              {/* Execution Status Indicator */}
              {executionStatus !== 'idle' && (
                <div className="flex items-center gap-2">
                  {executionStatus === 'running' && (
                    <>
                      <div className="loading loading-spinner loading-sm text-warning"></div>
                      <span className="text-sm text-warning font-medium">Running</span>
                    </>
                  )}
                  {executionStatus === 'success' && (
                    <>
                      <CheckCircle className="h-4 w-4 text-success" />
                      <span className="text-sm text-success font-medium">Completed</span>
                    </>
                  )}
                  {executionStatus === 'failed' && (
                    <>
                      <XCircle className="h-4 w-4 text-error" />
                      <span className="text-sm text-error font-medium">Failed</span>
                    </>
                  )}
                </div>
              )}
            </div>
            <button
              className={`btn ${isExecuting ? 'btn-disabled' : 'btn-primary'} text-white`}
              onClick={handleExecuteClick}
              disabled={isExecuting}
            >
              {isExecuting ? (
                <>
                  <div className="loading loading-spinner loading-sm mr-2"></div>
                  Executing...
                </>
              ) : (
                <>
                  <Play className="h-4 w-4 mr-2" /> Execute
                </>
              )}
            </button>
          </div>

          <section className="flex-1">
            {/* Full height container */}

            <div className="flex flex-col h-full bg-base-100">
              {/* Scrollable area */}
              <div className="flex-1 space-y-4">
                {workflow.length === 0 ? (
                  <div className="flex items-center rounded-lg border-2 border-dashed border-base-200 justify-center h-full text-gray-500">
                    No tasks in this workflow.
                  </div>
                ) : (
                  workflow.map((task) => (
                    <div
                      key={task.id}
                      className="card bg-base-100 shadow-md mb-2"
                      style={{
                        borderLeft: `4px solid ${getColorForType(task.type)}`,
                      }}
                    >
                      <div className="card-body p-4">
                        <div className="flex justify-between items-start mb-2">
                          <div className="text-lg font-semibold">
                            {task.content}
                          </div>
                          <div
                            className="flex gap-2 badge text-md"
                            style={{
                              backgroundColor: getColorForType(task.type),
                              color: "white",
                            }}
                          >
                            {task.type}
                          </div>
                        </div>
                        <ExecutableTask
                          config={task.config}
                          onUpdate={(newConfig) =>
                            handleTaskUpdate(task.id, newConfig)
                          }
                          availableTasks={workflow}
                          taskId={task.id}
                        />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </section>
        </div>

        {/* Right: Results Panel */}
        {showResults && (
          <ResultsSidebar
            executionStatus={executionStatus}
            dagRunDetails={dagRunDetails}
            executionResult={executionResult}
            isLoadingResults={isLoadingResults}
            output={output}
            onViewMoreInfo={dagRunDetails ? handleViewMoreInfo : undefined}
            onDownloadResults={handleDownloadResults}
            onClose={() => setShowResults(false)}
            onRunAgain={() => {
              setExecutionStatus('idle');
              setExecutionResult(null);
              setDagRunDetails(null);
              setShowResults(false);
            }}
          />
        )}
      </div>

      {/* Confirmation Modal */}
      <dialog ref={modalRef} className="modal">
        <div className="modal-box">
          <h3 className="font-bold text-lg">Confirm Workflow Execution</h3>
          <p className="py-4">
            Are you sure you want to execute this workflow with the following
            schedule?
          </p>
          {scheduleInfo && (
            <div className="bg-base-200 p-3 rounded-lg mb-4">
              <p className="font-medium">{scheduleInfo.schedule_text}</p>
              {scheduleInfo.type === 'multiple' && scheduleInfo.payload?.schedule && (
                <div className="mt-2">
                  <a
                    href={`https://crontab.guru/#${scheduleInfo.payload.schedule.replace(/ /g, "_")}`}
                    target="_blank"
                    className="link link-accent text-sm"
                  >
                    ↗ Preview on crontab.guru
                  </a>
                </div>
              )}
            </div>
          )}
          <div className="modal-action">
            <button className="btn btn-ghost" onClick={handleCancelExecution}>
              Cancel
            </button>
            <button
              className="btn btn-primary"
              onClick={handleConfirmExecution}
            >
              Confirm Execute
            </button>
          </div>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button onClick={handleCancelExecution}>close</button>
        </form>
      </dialog>

      {/* More Info Modal */}
      <dialog ref={moreInfoModalRef} className="modal">
        <div className="modal-box w-11/12 max-w-5xl h-5/6">
          <h3 className="font-bold text-lg mb-4">
            <FileText className="h-5 w-5 inline mr-2" />
            Task Details and Results
          </h3>
          
          {dagRunDetails?.task_instances && (
            <div className="space-y-4 h-full overflow-auto">
              {dagRunDetails.task_instances.map((taskInstance: any, index: number) => (
                <div key={index} className="card bg-base-200 shadow-sm">
                  <div className="card-body p-4">
                    <div className="flex justify-between items-center mb-2">
                      <h4 className="font-semibold">{taskInstance.task_id}</h4>
                      <span className={`badge ${
                        taskInstance.state === 'success' ? 'badge-success' :
                        taskInstance.state === 'failed' ? 'badge-error' :
                        'badge-warning'
                      }`}>
                        {taskInstance.state || 'unknown'}
                      </span>
                    </div>
                    
                    <div className="text-xs text-base-content/70 mb-2">
                      <div>Start: {taskInstance.start_date ? new Date(taskInstance.start_date).toLocaleString() : 'N/A'}</div>
                      <div>End: {taskInstance.end_date ? new Date(taskInstance.end_date).toLocaleString() : 'N/A'}</div>
                      <div>Duration: {taskInstance.duration ? `${taskInstance.duration}s` : 'N/A'}</div>
                    </div>
                    
                    {/* XCOM Values - Show all results */}
                    {taskInstance.xcom_entries?.length > 0 && (
                      <div className="mb-3">
                        <h5 className="font-semibold text-sm mb-1">Results (XCOM Values):</h5>
                        <div className="bg-base-100 p-2 rounded text-xs space-y-1">
                          {taskInstance.xcom_entries.map((xcom: any, xcomIndex: number) => (
                            <div key={xcomIndex} className="border-b border-base-200 pb-1 last:border-b-0">
                              <div className="font-mono text-accent font-semibold">{xcom.key}:</div>
                              <div className="font-mono text-sm mt-1 break-all">
                                {xcom.value == null 
                                  ? 'null'
                                  : typeof xcom.value === 'string' 
                                    ? xcom.value
                                    : JSON.stringify(xcom.value, null, 2)
                                }
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
          
          <div className="modal-action">
            <button 
              className="btn btn-ghost"
              onClick={() => moreInfoModalRef.current?.close()}
            >
              Close
            </button>
            <button 
              className="btn btn-primary"
              onClick={() => {
                handleDownloadResults();
                moreInfoModalRef.current?.close();
              }}
            >
              <Download className="h-4 w-4 mr-2" />
              Download All
            </button>
          </div>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button onClick={() => moreInfoModalRef.current?.close()}>close</button>
        </form>
      </dialog>
    </div>
  );
}
