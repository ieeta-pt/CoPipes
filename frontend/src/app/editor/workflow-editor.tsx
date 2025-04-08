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
      dag_id: "generated_dag",
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
