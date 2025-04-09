import React from "react"
import { BaseTask } from "@/components/airflow-tasks/BaseTask"
import { TaskConfig } from "@/components/airflow-tasks/types"

interface ToKVTaskProps {
  config: TaskConfig
  onUpdate: (newConfig: TaskConfig) => void
}

export const CSVTask: React.FC<ToKVTaskProps> = ({ config, onUpdate }) => {
  return (
    <div>
      <BaseTask config={config} onUpdate={onUpdate} />
    </div>
  )
}
