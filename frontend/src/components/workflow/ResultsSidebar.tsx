import React from "react";
import { CheckCircle, XCircle, Clock, Download, Eye } from "lucide-react";

interface ResultsSidebarProps {
  executionStatus: 'idle' | 'running' | 'success' | 'failed';
  dagRunDetails: any;
  executionResult: any;
  isLoadingResults: boolean;
  output: string;
  onViewMoreInfo?: () => void;
  onDownloadResults: () => void;
  onClose: () => void;
  onRunAgain: () => void;
}

export function ResultsSidebar({
  executionStatus,
  dagRunDetails,
  executionResult,
  isLoadingResults,
  output,
  onViewMoreInfo,
  onDownloadResults,
  onClose,
  onRunAgain
}: ResultsSidebarProps) {
  return (
    <div className="w-96 flex flex-col gap-4">
      <div className="card rounded-box bg-base-100 border border-base-200 shadow-lg h-full">
        <div className="card-body">
          <div className="flex items-center gap-2 mb-4">
            {executionStatus === 'success' && (
              <CheckCircle className="h-5 w-5 text-success" />
            )}
            {executionStatus === 'failed' && (
              <XCircle className="h-5 w-5 text-error" />
            )}
            {executionStatus === 'running' && (
              <Clock className="h-5 w-5 text-warning" />
            )}
            <h3 className="card-title text-lg">Execution Results</h3>
          </div>
          
          {/* Status Badge */}
          <div className="mb-4">
            <div className={`badge ${
              executionResult?.execution_result?.status === 'scheduled' ? 'badge-info' :
              dagRunDetails?.dag_run?.state === 'success' ? 'badge-success' :
              dagRunDetails?.dag_run?.state === 'failed' ? 'badge-error' :
              executionStatus === 'running' ? 'badge-warning' :
              'badge-info'
            } badge-lg`}>
              {executionResult?.execution_result?.status === 'scheduled' ? 'Scheduled' :
               dagRunDetails?.dag_run?.state || executionStatus}
            </div>
          </div>

          {/* Loading Results */}
          {isLoadingResults && (
            <div className="flex items-center gap-2 mb-4">
              <div className="loading loading-spinner loading-sm"></div>
              <span className="text-sm">Fetching execution details...</span>
            </div>
          )}

          {/* Output/Results */}
          <div className="flex flex-col gap-4 flex-1">
            {/* DAG Run Summary */}
            {dagRunDetails?.dag_run && (
              <div>
                <h4 className="font-semibold mb-2">Execution Summary:</h4>
                <div className="bg-base-200 p-3 rounded-lg text-sm">
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div><strong>Start:</strong> {dagRunDetails.dag_run.start_date ? new Date(dagRunDetails.dag_run.start_date).toLocaleString() : 'N/A'}</div>
                    <div><strong>End:</strong> {dagRunDetails.dag_run.end_date ? new Date(dagRunDetails.dag_run.end_date).toLocaleString() : 'N/A'}</div>
                  </div>
                </div>
              </div>
            )}

            {/* Task Results Summary - Only list tasks and their status */}
            {dagRunDetails?.task_instances && dagRunDetails.task_instances.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2">Task Results:</h4>
                <div className="bg-base-200 p-3 rounded-lg text-sm max-h-40 overflow-auto">
                  {dagRunDetails.task_instances.map((task: any, index: number) => (
                    <div 
                      key={index} 
                      className="mb-2 p-2 bg-base-100 rounded border-l-4" 
                      style={{borderLeftColor: task.state === 'success' ? '#10b981' : task.state === 'failed' ? '#ef4444' : '#f59e0b'}}
                    >
                      <div className="flex justify-between items-center">
                        <strong className="text-xs">{task.task_id}</strong>
                        <span className={`badge badge-xs ${
                          task.state === 'success' ? 'badge-success' :
                          task.state === 'failed' ? 'badge-error' :
                          'badge-warning'
                        }`}>{task.state}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Last Task Return Value - Only if exists */}
            {(() => {
              const lastTask = dagRunDetails?.task_instances?.[dagRunDetails.task_instances.length - 1];
              const returnValueXcom = lastTask?.xcom_entries?.find((xcom: any) => xcom.key === 'return_value');
              
              if (!returnValueXcom) return null;
              
              const displayValue = returnValueXcom.value == null 
                ? 'null'
                : typeof returnValueXcom.value === 'string' 
                  ? returnValueXcom.value.slice(0, 200) + (returnValueXcom.value.length > 200 ? '...' : '')
                  : (() => {
                      const stringified = JSON.stringify(returnValueXcom.value, null, 2);
                      return stringified.slice(0, 200) + (stringified.length > 200 ? '...' : '');
                    })();
              
              return (
                <div className="mt-3 p-2 bg-primary/10 border border-primary/20 rounded-lg">
                  <div className="font-semibold text-primary text-sm mb-2">
                    Workflow Result ({lastTask.task_id}):
                  </div>
                  <div className="text-xs">
                    <div className="bg-base-100 p-2 rounded">
                      <div className="font-mono text-accent font-semibold">return_value:</div>
                      <div className="font-mono text-sm mt-1 break-all">
                        {displayValue}
                      </div>
                      {((typeof returnValueXcom.value === 'string' && returnValueXcom.value.length > 200) || 
                        (typeof returnValueXcom.value !== 'string' && JSON.stringify(returnValueXcom.value).length > 200)) && (
                        <div className="text-xs text-gray-500 mt-1 italic">
                          View "More info" for complete output
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              );
            })()}

            {/* Basic Output (fallback) */}
            {output && !dagRunDetails && (
              <div>
                <div className="bg-base-200 p-3 rounded-lg text-sm overflow-auto max-h-40">
                  <pre className="whitespace-pre-wrap font-mono text-xs">
                    {output}
                  </pre>
                </div>
              </div>
            )}

            {/* Error Details */}
            {/* {executionStatus === 'failed' && (
              <div>
                <h4 className="font-semibold mb-2 text-error">Error Details:</h4>
                <div className="bg-error/10 border border-error/20 p-3 rounded-lg text-sm">
                  <pre className="whitespace-pre-wrap text-error">
                    {executionResult?.error || 
                     (dagRunDetails?.task_instances?.find((t: any) => t.state === 'failed')?.logs?.content) ||
                     "Unknown error occurred"}
                  </pre>
                </div>
              </div>
            )} */}
          </div>

          {/* Actions */}
          <div className="card-actions justify-between mt-4">
            <div className="flex gap-2">
              {/* View More Info */}
              {onViewMoreInfo && executionResult?.execution_result?.dag_run_id && (
                <button 
                  className="btn btn-ghost btn-sm"
                  onClick={onViewMoreInfo}
                  disabled={isLoadingResults}
                >
                  <Eye className="h-3 w-3 mr-1" />
                  More info
                </button>
              )}
              
              {/* Download Results - Hide for scheduled workflows */}
              {(dagRunDetails || executionResult) && executionResult?.execution_result?.status !== 'scheduled' && (
                <button 
                  className="btn btn-ghost btn-sm"
                  onClick={onDownloadResults}
                >
                  <Download className="h-3 w-3 mr-1" />
                  Download
                </button>
              )}
            </div>
            
            <div className="flex gap-2">
              <button 
                className="btn btn-ghost btn-sm"
                onClick={onClose}
              >
                Close
              </button>
              {executionStatus === 'success' && executionResult?.execution_result?.status !== 'scheduled' && (
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={onRunAgain}
                >
                  Run Again
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}