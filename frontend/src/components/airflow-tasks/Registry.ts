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
    component: BaseTask,
  },
  "To key value": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "filename", value: "", type: "string" },
    ],
    component: BaseTask,
  },
  "Harmonize": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "filename", value: "", type: "string" },
    ],
    component: BaseTask,
  },
  "Migrate": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "filename", value: "", type: "string" },
    ],
    component: BaseTask,
  },
  "Create connection": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { name: "filename", value: "", type: "string" },
    ],
    component: BaseTask,
  },
  "Create table": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { name: "filename", value: "", type: "string" },
    ],
    component: BaseTask,
  },
  "Write to DB": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { name: "filename", value: "", type: "string" },
    ],
    component: BaseTask,
  },
}
