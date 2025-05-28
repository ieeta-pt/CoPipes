// taskRegistry.ts
import { TaskRegistry } from "@/components/airflow-tasks/types"
import { BaseTask } from "@/components/airflow-tasks/BaseTask"

export const Registry: TaskRegistry = {
  "CSV": {
    type: "Extraction",
    defaultConfig: [
      { 
        name: "filename", 
        value: "", 
        type: "file",
        placeholder: "File to read",
        required: true,
        validation: { message: "Filename is required" }
      },
      { 
        name: "file separation", 
        value: "Comma", 
        type: "select",
        options: ["Comma", "Semicolon", "Tab"],
        placeholder: "Select file separator",
        required: false
      }
    ],
    component: BaseTask,
  },
  "To key value": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data to reorganize (CSV extraction result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "fixed columns", 
        value: "", 
        type: "string", 
        placeholder: "List of fixed columns names (separated by commas)",
        required: false
      },
      { 
        name: "measurement columns", 
        value: "", 
        type: "string", 
        placeholder: "List of measurement columns (separated by commas)",
        required: false
      },
    ],
    component: BaseTask,
  },
  "Harmonize": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data to harmonize (To key value result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "mappings", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data mappings (CSV extraction result or file)",
        required: true,
        validation: { message: "Mappings are required" }
      },
      { 
        name: "adhoc harmonization", 
        value: "False", 
        type: "boolean",
        placeholder: "Enable ad-hoc harmonization rules",
        required: false
      },
    ],
    component: BaseTask,
  },
  "Migrate": {
    type: "Transformation",
    subtype: "Cohorts",
    defaultConfig: [
      { 
        name: "person data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data for personal information table (CSV extraction result)",
        required: true,
        validation: { message: "Person data is required" }
      },
      { 
        name: "observation data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data for observation table (Harmonize result)",
        required: true,
        validation: { message: "Observation data is required" }
      },
      { 
        name: "mappings", 
        value: "", 
        type: "task_reference", 
        placeholder: "Data mappings (CSV extraction result or file)",
        required: true,
        validation: { message: "Mappings are required" }
      },
      { 
        name: "adhoc migration", 
        value: "False", 
        type: "boolean",
        placeholder: "Enable ad-hoc migration rules",
        required: false
      },
    ],
    component: BaseTask,
  },
  "Create connection": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { 
        name: "connection id", 
        value: "my_postgres", 
        type: "string",
        placeholder: "Connection identifier",
        required: false
      },
      { 
        name: "host", 
        value: "postgres", 
        type: "string",
        placeholder: "Database host",
        required: false
      },
      { 
        name: "schema", 
        value: "airflow", 
        type: "string",
        placeholder: "Database schema",
        required: false
      },
      { 
        name: "login", 
        value: "airflow", 
        type: "string",
        placeholder: "Database username",
        required: false
      },
      { 
        name: "password", 
        value: "airflow", 
        type: "string",
        placeholder: "Database password",
        required: false
      },
      { 
        name: "port", 
        value: "5432", 
        type: "string",
        placeholder: "Database port",
        required: false,
        validation: { pattern: "^[0-9]+$", message: "Port must be a number" }
      }
    ],
    component: BaseTask,
  },
  "Create table": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { 
        name: "columns", 
        value: "", 
        type: "string", 
        placeholder: "List of columns (separated by commas)",
        required: true,
        validation: { message: "Column list is required" }
      },
      { 
        name: "table name", 
        value: "", 
        type: "string", 
        placeholder: "My table",
        required: true,
        validation: { message: "Table name is required" }
      },
    ],
    component: BaseTask,
  },
  "Write to DB": {
    type: "Loading",
    subtype: "Postgres",
    defaultConfig: [
      { 
        name: "data", 
        value: "", 
        type: "task_reference", 
        placeholder: "Table contents (Migrate result)",
        required: true,
        validation: { message: "Data input is required" }
      },
      { 
        name: "table name", 
        value: "", 
        type: "string", 
        placeholder: "My table",
        required: true,
        validation: { message: "Table name is required" }
      },
      { 
        name: "connection id", 
        value: "my_postgres", 
        type: "string",
        placeholder: "Connection identifier",
        required: false
      }
    ],
    component: BaseTask,
  },
}
