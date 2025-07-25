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

export function WorkflowCanvas({
  workflowItems,
  setWorkflowItems,
  readOnly = false,
}: {
  workflowItems: WorkflowComponent[];
  setWorkflowItems: (items: WorkflowComponent[]) => void;
  onCompile: () => void;
  readOnly?: boolean;
}) {
  const [activeItem, setActiveItem] = useState<WorkflowComponent | null>(null);

  const sensors = useSensors(useSensor(PointerSensor));

  const handleDragStart = (event: DragStartEvent) => {
    if (readOnly) return;
    const item = workflowItems.find((i) => i.id === event.active.id);
    if (item) setActiveItem(item);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    if (readOnly) return;
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
          {/* Scrollable area */}
          <div className="flex flex-col h-full bg-base-100 flex-1 space-y-4">
            {workflowItems.length === 0 ? (
              <div className="flex items-center  rounded-lg border-2 border-dashed border-base-200 justify-center h-full text-gray-500">
                Select a task from the sidebar to begin.
              </div>
            ) : (
              workflowItems.map((item, index) => (
                <SortableItem
                  key={item.id}
                  item={item}
                  readOnly={readOnly}
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
