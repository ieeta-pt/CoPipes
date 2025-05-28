export type ConfigFieldType = "string" | "file" | "boolean" | "radio" | "select" | "task_reference"

export interface ConfigField {
  name: string
  value: string
  type: ConfigFieldType
  options?: string[]
  placeholder?: string
  required?: boolean
  validation?: {
    pattern?: string
    min?: number
    max?: number
    message?: string
  }
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
  schedule?: string
  start_date?: string
  tasks: WorkflowComponent[]
}
