// taskRegistry.ts
import { CSVTask } from "@/components/airflow-tasks/tasks/CSVTask"
import { TaskRegistry } from "@/components/airflow-tasks/types"
import { BaseTask } from "./BaseTask"

export const Registry: TaskRegistry = {
  "CSV": {
    type: "Extraction",
    defaultConfig: [
      { name: "filename", value: "", type: "file" },
      { name: "file_sep", value: ",", type: "string" }
    ],
    component: CSVTask,
  },
  "Harmonizer": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "filename", value: "", type: "string" },
    ],
    component: BaseTask,
  },
}
