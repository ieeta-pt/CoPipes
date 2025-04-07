export type ConfigFieldType = "string" | "file"

export interface TaskConfigField {
  name: string
  value: string
  type: ConfigFieldType
}

export type TaskConfig = TaskConfigField[]

export interface WorkflowItem {
  id: string
  content: string
  type: string
  config: TaskConfig
}

export interface TaskRegistryEntry {
  type: string
  defaultConfig: TaskConfig
  component: React.FC<{
    config: TaskConfig
    onUpdate: (newConfig: TaskConfig) => void
  }>
}

export type TaskRegistry = Record<string, TaskRegistryEntry>
