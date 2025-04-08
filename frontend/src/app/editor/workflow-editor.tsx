"use client";

import { useState } from "react";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  DragOverlay,
  DragStartEvent,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  arrayMove,
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { restrictToVerticalAxis } from "@dnd-kit/modifiers";
import { Download, Play } from "lucide-react";

import { Registry } from "@/components/airflow-tasks/Registry";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { SortableItem } from "@/app/editor/SortableItem";
import { submitWorkflow } from "@/api/workflow/test";

function groupTasksByType() {
  return Object.entries(
    Object.values(Registry).reduce((acc, task) => {
      if (!acc[task.type]) acc[task.type] = [];
      const taskName = Object.keys(Registry).find(
        (key) => Registry[key] === task
      );
      if (taskName) acc[task.type].push(taskName);
      return acc;
    }, {} as Record<string, string[]>)
  ).map(([name, items]) => ({ name, items }));
}

const componentCategories = groupTasksByType();

function createIdBuilder(prefix: string = "id") {
  let counter = 0;
  return `${prefix}_${++counter}`;
}

export default function WorkflowEditor() {
  const [workflowItems, setWorkflowItems] = useState<WorkflowComponent[]>([]);
  const [input, setInput] = useState("");
  const [output, setOutput] = useState("");
  const [activeItem, setActiveItem] = useState<WorkflowComponent | null>(null);

  const sensors = useSensors(useSensor(PointerSensor));

  const addComponent = (content: string, type: string) => {
    const taskDef = Registry[content];
    const newItem: WorkflowComponent = {
      id: createIdBuilder(content),
      content,
      type,
      config: [...taskDef.defaultConfig],
    };
    setWorkflowItems([...workflowItems, newItem]);
  };

  const removeComponent = (id: string) => {
    setWorkflowItems(workflowItems.filter((item) => item.id !== id));
  };

  const handleDragStart = (event: DragStartEvent) => {
    const { active } = event;
    const item = workflowItems.find((i) => i.id === active.id);
    if (item) {
      setActiveItem(item);
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = workflowItems.findIndex((item) => item.id === active.id);
      const newIndex = workflowItems.findIndex((item) => item.id === over?.id);
      setWorkflowItems(arrayMove(workflowItems, oldIndex, newIndex));
    }
    setActiveItem(null);
  };

  const testWorkflow = async () => {
    const payload = {
      dag_id: "test_dag",
      tasks: workflowItems,
    };

    try {
      const result = await submitWorkflow(payload);
      setOutput(JSON.stringify(result, null, 2));
    } catch (err) {
      console.error(err);
      setOutput("❌ Failed to submit workflow");
    }
  };

  const downloadWorkflow = () => {
    const workflowData = { tasks: workflowItems, input, output };
    const blob = new Blob([JSON.stringify(workflowData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "workflow.json";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-base-200 border-r border-base-300 flex flex-col">
        <div className="p-4 text-2xl font-bold">LOGO</div>
        <div className="flex-1 overflow-auto">
          {componentCategories.map((category) => (
            <div key={category.name} className="collapse collapse-arrow">
              <input type="checkbox" />
              <div className="collapse-title font-medium">{category.name}</div>
              <div className="collapse-content">
                {category.items.map((item) => (
                  <div
                    key={item}
                    className="btn btn-sm btn-ghost w-full justify-start"
                    onClick={() => addComponent(item, category.name)}
                  >
                    {item}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </aside>

      <main className="flex-1 flex flex-col overflow-hidden">
        <div className="p-4 border-b border-base-300">
          <h1 className="text-2xl font-bold">Workflow</h1>
        </div>

        <div className="flex-1 flex overflow-hidden">
          <section className="flex-1 overflow-auto p-6">
            <DndContext
              sensors={sensors}
              collisionDetection={closestCenter}
              onDragStart={handleDragStart}
              onDragEnd={handleDragEnd}
              modifiers={[restrictToVerticalAxis]}
            >
              <SortableContext
                items={workflowItems.map((item) => item.id)}
                strategy={verticalListSortingStrategy}
              >
                <div className="min-h-full flex flex-col gap-4">
                  {workflowItems.map((item, index) => (
                    <SortableItem
                      key={item.id}
                      item={item}
                      onRemove={removeComponent}
                      onUpdate={(newConfig) => {
                        const updated = [...workflowItems];
                        updated[index].config = newConfig;
                        setWorkflowItems(updated);
                      }}
                    />
                  ))}
                  <div className="flex justify-center mt-6 gap-4 mt-auto p-4">
                    <button onClick={testWorkflow} className="btn btn-primary">
                      <Play className="h-4 w-4 mr-2" /> Test
                    </button>
                    <button
                      onClick={downloadWorkflow}
                      className="btn btn-secondary"
                    >
                      <Download className="h-4 w-4 mr-2" /> Download
                    </button>
                  </div>
                </div>
              </SortableContext>
              <DragOverlay>
                {activeItem && (
                  <SortableItem
                    item={activeItem}
                    isOverlay
                    onRemove={() => {}}
                    onUpdate={() => {}}
                  />
                )}
              </DragOverlay>
            </DndContext>
          </section>

          <aside className="w-80 border-l border-base-300 p-4 flex flex-col">
            <div className="flex-1">
              <h3 className="font-semibold mb-2">Input</h3>
              <textarea
                className="textarea textarea-bordered w-full h-[200px]"
                placeholder="Enter input data..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
              ></textarea>
            </div>
            <div className="divider"></div>
            <div className="flex-1">
              <h3 className="font-semibold mb-2">Output</h3>
              <textarea
                className="textarea textarea-bordered w-full h-[200px]"
                placeholder="Output will appear here..."
                value={output}
                readOnly
              ></textarea>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}

// "use client"

// import { useState } from "react"
// import {
//   DndContext,
//   closestCenter,
//   PointerSensor,
//   useSensor,
//   useSensors,
//   DragOverlay,
//   DragStartEvent,
//   DragEndEvent,
// } from "@dnd-kit/core"
// import {
//   arrayMove,
//   SortableContext,
//   useSortable,
//   verticalListSortingStrategy,
// } from "@dnd-kit/sortable"
// import { restrictToVerticalAxis } from "@dnd-kit/modifiers"
// import { CSS } from "@dnd-kit/utilities"
// import { X, Download, Play, GripVertical } from "lucide-react"

// const componentCategories = [
//   { name: "Extraction", items: ["Extraction 1", "Extraction 2"] },
//   { name: "Transformation", items: ["Transformation 1", "Transformation 2", "Transformation 3"] },
//   { name: "Loading", items: ["Load 1", "Load 2"] },
//   { name: "Analysis", items: ["Analysis 1", "Analysis 2"] },
//   { name: "General", items: ["LLM", "Custom"] },
// ]

// const componentParams = {
//   LLM: [
//     { name: "Param: xpto", value: "" },
//     { name: "Param: xpto", value: "" },
//     { name: "Param: xpto", value: "" },
//   ],
// }

// type WorkflowComponent = {
//   id: string
//   content: string
//   type: string
// }

// export default function WorkflowEditor() {
//   const [workflowItems, setWorkflowItems] = useState<WorkflowComponent[]>([
//     { id: "item-1", content: "Extraction 2", type: "Extraction" },
//     { id: "item-2", content: "Transformation 2", type: "Transformation" },
//     { id: "item-3", content: "Transformation 3", type: "Transformation" },
//     { id: "item-4", content: "Load 2", type: "Loading" },
//     { id: "item-5", content: "LLM", type: "General" },
//   ])

//   const [input, setInput] = useState("")
//   const [output, setOutput] = useState("")
//   const [activeItem, setActiveItem] = useState<WorkflowComponent | null>(null)

//   const sensors = useSensors(useSensor(PointerSensor))

//   const addComponent = (content: string, type: string) => {
//     const newItem = { id: `item-${crypto.randomUUID()}`, content, type }
//     setWorkflowItems([...workflowItems, newItem])
//   }

//   const removeComponent = (id: string) => {
//     setWorkflowItems(workflowItems.filter((item) => item.id !== id))
//   }

//   const handleDragStart = (event: DragStartEvent) => {
//     const { active } = event
//     const item = workflowItems.find((i) => i.id === active.id)
//     if (item) {
//       setActiveItem(item)
//     }
//   }

//   const handleDragEnd = (event: DragEndEvent) => {
//     const { active, over } = event

//     if (active.id !== over?.id) {
//       const oldIndex = workflowItems.findIndex((item) => item.id === active.id)
//       const newIndex = workflowItems.findIndex((item) => item.id === over?.id)
//       setWorkflowItems(arrayMove(workflowItems, oldIndex, newIndex))
//     }

//     setActiveItem(null)
//   }

//   const testWorkflow = () => {
//     setOutput(`Test results for workflow with ${workflowItems.length} components`)
//   }

//   const downloadWorkflow = () => {
//     const workflowData = { components: workflowItems, input, output }
//     const blob = new Blob([JSON.stringify(workflowData, null, 2)], { type: "application/json" })
//     const url = URL.createObjectURL(blob)
//     const a = document.createElement("a")
//     a.href = url
//     a.download = "workflow.json"
//     document.body.appendChild(a)
//     a.click()
//     document.body.removeChild(a)
//     URL.revokeObjectURL(url)
//   }

//   return (
//     <div className="flex h-screen">
//       <aside className="w-64 bg-base-200 border-r border-base-300 flex flex-col">
//         <div className="p-4 text-2xl font-bold">LOGO</div>
//         <div className="flex-1 overflow-auto">
//           {componentCategories.map((category) => (
//             <div key={category.name} className="collapse collapse-arrow">
//               <input type="checkbox" />
//               <div className="collapse-title font-medium">{category.name}</div>
//               <div className="collapse-content">
//                 {category.items.map((item) => (
//                   <div
//                     key={item}
//                     className="btn btn-sm btn-ghost w-full justify-start"
//                     onClick={() => addComponent(item, category.name)}
//                   >
//                     {item}
//                   </div>
//                 ))}
//               </div>
//             </div>
//           ))}
//         </div>
//         {/* <div className="p-4 border-t border-base-300 text-sm">
//           <div className="font-medium">Profile Name</div>
//           <div className="text-base-content/70">View profile</div>
//         </div> */}
//       </aside>

//       <main className="flex-1 flex flex-col overflow-hidden">
//         <div className="p-4 border-b border-base-300">
//           <h1 className="text-2xl font-bold">Workflow</h1>
//         </div>

//         <div className="flex-1 flex overflow-hidden">
//           <section className="flex-1 overflow-auto p-6">
//             <DndContext
//               sensors={sensors}
//               collisionDetection={closestCenter}
//               onDragStart={handleDragStart}
//               onDragEnd={handleDragEnd}
//               modifiers={[restrictToVerticalAxis]}
//             >
//               <SortableContext
//                 items={workflowItems.map((item) => item.id)}
//                 strategy={verticalListSortingStrategy}
//                 >
//                 <div className="min-h-full flex flex-col">
//                     <div className="space-y-4">
//                     {workflowItems.map((item) => (
//                         <SortableItem
//                         key={item.id}
//                         item={item}
//                         remove={removeComponent}
//                         />
//                     ))}
//                     </div>

//                     <div className="flex justify-center mt-6 gap-4 mt-auto p-4">
//                     <button onClick={testWorkflow} className="btn btn-primary">
//                         <Play className="h-4 w-4 mr-2" /> Test
//                     </button>
//                     <button onClick={downloadWorkflow} className="btn btn-secondary">
//                         <Download className="h-4 w-4 mr-2" /> Download
//                     </button>
//                     </div>
//                 </div>
//                 </SortableContext>
//                 <DragOverlay>
//                 {activeItem ? (
//                     <SortableItem
//                     item={activeItem}
//                     remove={() => {}}
//                     isOverlay
//                     />
//                 ) : null}
//                 </DragOverlay>

//             </DndContext>
//           </section>

//           <aside className="w-80 border-l border-base-300 p-4 flex flex-col">
//             <div className="flex-1">
//               <h3 className="font-semibold mb-2">Input</h3>
//               <textarea
//                 className="textarea textarea-bordered w-full h-[200px]"
//                 placeholder="Enter input data..."
//                 value={input}
//                 onChange={(e) => setInput(e.target.value)}
//               ></textarea>
//             </div>
//             <div className="divider"></div>
//             <div className="flex-1">
//               <h3 className="font-semibold mb-2">Output</h3>
//               <textarea
//                 className="textarea textarea-bordered w-full h-[200px]"
//                 placeholder="Output will appear here..."
//                 value={output}
//                 readOnly
//               ></textarea>
//             </div>
//           </aside>
//         </div>
//       </main>
//     </div>
//   )
// }

// interface SortableItemProps {
//     item: WorkflowComponent
//     remove: (id: string) => void
//     isOverlay?: boolean
//   }

// function SortableItem({ item, remove, isOverlay = false }: SortableItemProps) {
//     const {
//       attributes,
//       listeners,
//       setNodeRef,
//       transform,
//       transition,
//     } = useSortable({ id: item.id })

//     const style = {
//       transform: CSS.Transform.toString(transform),
//       transition,
//       borderLeft: `4px solid ${getColorForType(item.type)}`,
//       opacity: isOverlay ? 0.8 : 1,
//       cursor: isOverlay ? "grabbing" : "default",
//       zIndex: isOverlay ? 999 : "auto",
//     }

//     return (
//       <div
//         ref={setNodeRef}
//         style={style}
//         className={`card bg-base-100 shadow-md ${isOverlay ? "pointer-events-none" : ""}`}
//       >
//         <div className="card-body p-4">
//           <div className="flex justify-between items-start">
//             <div className="font-medium">{item.content}</div>
//             {!isOverlay && (
//               <div className="flex gap-2">
//                 <button
//                   className="btn btn-xs btn-soft btn-secondary cursor-grab"
//                   {...listeners}
//                   {...attributes}
//                 >
//                   <GripVertical className="h-4 w-4" />
//                 </button>
//                 <button
//                   className="btn btn-xs btn-soft btn-error"
//                   onClick={(e) => {
//                     e.stopPropagation()
//                     remove(item.id)
//                   }}
//                 >
//                   <X className="h-4 w-4" />
//                 </button>
//               </div>
//             )}
//           </div>

//           {componentParams[item.content as keyof typeof componentParams] && (
//             <div className="mt-3 space-y-2">
//               {componentParams[item.content as keyof typeof componentParams].map((param, i) => (
//                 <div key={i} className="text-sm text-base-content/70">
//                   {param.name}
//                 </div>
//               ))}
//             </div>
//           )}
//         </div>
//       </div>
//     )
//   }

// function getColorForType(type: string): string {
//   const colors: Record<string, string> = {
//     Extraction: "#3b82f6",
//     Transformation: "#10b981",
//     Loading: "#f59e0b",
//     Analysis: "#8b5cf6",
//     General: "#6b7280",
//   }
//   return colors[type] || "#6b7280"
// }
