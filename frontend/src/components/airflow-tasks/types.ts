export type ConfigFieldType = "string" | "file"

export interface ConfigField {
  name: string
  value: string
  type: ConfigFieldType
}

export type TaskConfig = ConfigField[]

export interface TaskRegistryEntry {
  type: string
  subtype?: string
  defaultConfig: TaskConfig
  component: React.FC<{
    config: TaskConfig
    onUpdate: (newConfig: TaskConfig) => void
  }>
  description?: string
}

export type TaskRegistry = Record<string, TaskRegistryEntry>

export interface WorkflowComponent {
  id: string
  content: string
  type: string
  subtype?: string
  config: TaskConfig
  dependencies?: string[]
}

export interface WorkflowRequest {
  dag_id: string
  schedule_interval?: string
  start_date?: string
  tasks: WorkflowComponent[]
}
