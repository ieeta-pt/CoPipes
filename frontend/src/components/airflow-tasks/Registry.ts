// taskRegistry.ts
import { TaskRegistry } from "@/components/airflow-tasks/types"
import { BaseTask } from "@/components/airflow-tasks/BaseTask"

export const Registry: TaskRegistry = {
  "CSV": {
    type: "Extraction",
    defaultConfig: [
      { name: "filename", value: "File to read", type: "file" },
      { 
        name: "file separation", 
        value: "Comma", 
        type: "select",
        options: ["Comma", "Semicolon", "Tab"]
      }
    ],
    component: BaseTask,
  },
  "To key value": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "data", value: "Data to reorganize (CSV extraction result)", type: "string" },
      { name: "fixed columns", value: "List of fixed columns names (separated by commas)", type: "string" },
      { name: "measurement columns", value: "List of measurement columns (separated by commas)", type: "string" },
    ],
    component: BaseTask,
  },
  "Harmonize": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "data", value: "Data to harmonize (To key value result)", type: "string" },
      { name: "mappings", value: "Data mappings (CSV extraction result or file)", type: "string" },
      { 
        name: "adhoc harmonization", 
        value: "False", 
        type: "boolean"
      },
    ],
    component: BaseTask,
  },
  "Migrate": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { name: "person data", value: "Data for personal information table (CSV extraction result)", type: "string" },
      { name: "observation data", value: "Data for personal information table (Harmonize result)", type: "string" },
      { name: "mappings", value: "Data mappings (CSV extraction result or file)", type: "string" },
      { 
        name: "adhoc migration", 
        value: "False", 
        type: "boolean"
      },
    ],
    component: BaseTask,
  },
  "Create connection": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
    ],
    component: BaseTask,
  },
  "Create table": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { name: "columns", value: "List of columns (separated by commas)", type: "string" },
      { name: "table name", value: "My table", type: "string" },
    ],
    component: BaseTask,
  },
  "Write to DB": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { name: "data", value: "Table contents (Migrate result)", type: "string" },
      { name: "table name", value: "My table", type: "string" },
    ],
    component: BaseTask,
  },
}
