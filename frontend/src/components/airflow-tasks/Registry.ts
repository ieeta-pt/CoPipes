// taskRegistry.ts
import { CSVTask } from "@/components/airflow-tasks/tasks/CSVTask"
import { TaskRegistry } from "@/components/airflow-tasks/types"
import { BaseTask } from "./BaseTask"

export const Registry: TaskRegistry = {
  "CSV": {
    type: "Extraction",
    defaultConfig: [
      { name: "filename", value: "", type: "file" },
      { name: "file separation", value: ",", type: "string" }
    ],
    component: BaseTask,
  },
  "To key value": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "data", value: "Data to reorganize", type: "string" },
      { name: "fixed columns", value: "List of fixed columns names", type: "string" },
      { name: "measurement columns", value: "List of measurement columns", type: "string" },
    ],
    component: BaseTask,
  },
  "Harmonize": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "data", value: "Data to harmonize", type: "string" },
      { name: "mappings", value: "Data mappings", type: "string" },
      { name: "adhoc harmonization", value: "True / False", type: "string" },
    ],
    component: BaseTask,
  },
  "Migrate": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "person data", value: "Data for personal information table", type: "string" },
      { name: "observation data", value: "Data for personal information table", type: "string" },
      { name: "mappings", value: "Data mappings", type: "string" },
      { name: "adhoc migration", value: "True / False", type: "string" },
    ],
    component: BaseTask,
  },
  "Create connection": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { name: "database name", value: "My database", type: "string" },
    ],
    component: BaseTask,
  },
  "Create table": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { name: "columns", value: "List of columns", type: "string" },
      { name: "table name", value: "My table", type: "string" },
    ],
    component: BaseTask,
  },
  "Write to DB": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { name: "data", value: "Table contents", type: "string" },
      { name: "table name", value: "My table", type: "string" },
    ],
    component: BaseTask,
  },
}
