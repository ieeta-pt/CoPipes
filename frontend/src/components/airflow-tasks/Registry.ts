// taskRegistry.ts
import { CSVTask } from "@/components/airflow-tasks/tasks/CSVTask"
import { TaskRegistry } from "@/components/airflow-tasks/types"

export const Registry: TaskRegistry = {
  "from CSV": {
    type: "Extract",
    defaultConfig: [
      { name: "filename", value: "", type: "file" },
      { name: "file_sep", value: ",", type: "string" }
    ],
    component: CSVTask,
  },
}
