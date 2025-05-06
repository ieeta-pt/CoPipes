import { WorkflowTableWrapper } from "@/components/dashboard/workflow-table-wrapper"

// async function getData(): Promise<Workflow[]> {
//   // Fetch data from your API here.
//   return [
//     {
//       id: "728ed52f",
//       name: "Workflow 1",
//       last_edit: "2023-10-01",
//       last_run: "2023-10-02",
//       last_run_status: "Success",
//       people: ["Alice", "Bob"],
//     },
//     {
//       id: "728ed52f",
//       name: "Workflow 1",
//       last_edit: "2023-10-01",
//       last_run: "2023-10-02",
//       last_run_status: "Success",
//       people: ["Alice", "Bob"],
//     },{
//       id: "728ed52f",
//       name: "Workflow 1",
//       last_edit: "2023-10-01",
//       last_run: "2023-10-02",
//       last_run_status: "Success",
//       people: ["Alice", "Bob"],
//     },{
//       id: "728ed52f",
//       name: "1",
//       last_edit: "2023-10-01",
//       last_run: "2023-10-02",
//       last_run_status: "Success",
//       people: ["Alice", "Bob"],
//     },{
//       id: "728ed52f",
//       name: "Workflow 1",
//       last_edit: "2023-10-01",
//       last_run: "2023-10-02",
//       last_run_status: "Success",
//       people: ["Alice", "Bob"],
//     },
//   ]
// }

export default async function TablePage() {

  return (
    <div className="container mx-auto py-10">
      <WorkflowTableWrapper />
    </div>
  )
}
