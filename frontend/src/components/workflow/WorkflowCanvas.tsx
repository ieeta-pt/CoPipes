"use client";

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
import { useState } from "react";

import { SortableItem } from "@/components/workflow/SortableItem";
import { WorkflowComponent } from "@/components/airflow-tasks/types";
import { Settings } from "lucide-react";

export function WorkflowCanvas({
  workflowItems,
  setWorkflowItems,
  onCompile,
}: {
  workflowItems: WorkflowComponent[];
  setWorkflowItems: (items: WorkflowComponent[]) => void;
  onCompile: () => void;
}) {
  const [activeItem, setActiveItem] = useState<WorkflowComponent | null>(null);

  const sensors = useSensors(useSensor(PointerSensor));

  const handleDragStart = (event: DragStartEvent) => {
    const item = workflowItems.find((i) => i.id === event.active.id);
    if (item) setActiveItem(item);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (active.id !== over?.id) {
      const oldIndex = workflowItems.findIndex((i) => i.id === active.id);
      const newIndex = workflowItems.findIndex((i) => i.id === over?.id);
      setWorkflowItems(arrayMove(workflowItems, oldIndex, newIndex));
    }
    setActiveItem(null);
  };

  return (
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
        {/* Full height container */}
        <div className="flex flex-col h-full bg-base-100">
          {/* Scrollable area */}
          <div className="flex-1 space-y-4">
            {workflowItems.length === 0 ? (
              <div className="flex items-center  rounded-lg border-2 border-dashed border-base-200 justify-center h-full text-gray-500">
                Select a task from the sidebar to begin.
              </div>
            ) : (
              workflowItems.map((item, index) => (
                <SortableItem
                  key={item.id}
                  item={item}
                  onRemove={(id) =>
                    setWorkflowItems(workflowItems.filter((i) => i.id !== id))
                  }
                  onUpdate={(newConfig) => {
                    const updated = [...workflowItems];
                    updated[index].config = newConfig;
                    setWorkflowItems(updated);
                  }}
                />
              ))
            )}
          </div>

          {/* Button stays pinned to bottom */}
          <div className="flex justify-center mt-4">
            <button
              disabled={workflowItems.length === 0}
              className="btn btn-primary"
              onClick={onCompile}
            >
              <Settings className="h-4 w-4 mr-2" /> Compile
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
  );
}
