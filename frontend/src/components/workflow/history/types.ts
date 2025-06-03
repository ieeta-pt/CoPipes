export interface WorkflowRun {
  dag_run_id: string;
  execution_date: string;
  start_date: string;
  end_date: string;
  state: "success" | "failed" | "running" | "queued";
  run_type: string;
  external_trigger: boolean;
}

export interface TaskInstance {
  task_id: string;
  state: string;
  start_date: string;
  end_date: string;
  duration: number;
  // logs?: any;
  xcom_entries?: any[];
}

export interface RunDetailsData {
  dag_run: WorkflowRun;
  task_instances: TaskInstance[];
}