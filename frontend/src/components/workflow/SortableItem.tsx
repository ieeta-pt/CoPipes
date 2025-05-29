import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { X, GripVertical } from "lucide-react";
import { WorkflowComponent } from "@/components/airflow-tasks/types";

type Props = {
  item: WorkflowComponent;
  onRemove: (id: string) => void;
  onUpdate: (config: WorkflowComponent["config"]) => void;
  isOverlay?: boolean;
};

export const SortableItem: React.FC<Props> = ({
  item,
  onRemove,
  onUpdate,
  isOverlay = false,
}) => {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: item.id });
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    borderLeft: `4px solid ${getColorForType(item.type)}`,
    opacity: isOverlay ? 0.8 : 1,
    cursor: isOverlay ? "grabbing" : "default",
    zIndex: isOverlay ? 999 : "auto",
  };


  return (
    <div ref={setNodeRef} style={style} className="card bg-base-100 shadow-md mb-2">
      <div className="card-body p-4">
        <div className="flex justify-between items-start mb-2">
          <div className="text-lg font-semibold">{item.content}</div>
          {!isOverlay && (
            <div className="flex gap-2">
              <button
                className="btn btn-xs btn-soft btn-secondary cursor-grab"
                {...listeners}
                {...attributes}
              >
                <GripVertical className="h-4 w-4" />
              </button>
              <button
                className="btn btn-xs btn-error btn-soft"
                onClick={() => onRemove(item.id)}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 p-4 bg-base-100 rounded-lg min-w-0">
          {item.config.map((field) => (
            <div
              key={field.name}
              className="flex flex-col p-3 bg-white rounded border border-gray-200 shadow-sm"
            >
              <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">
                {field.name}
              </span>
              <span className="text-sm text-gray-900 whitespace-pre-line break-normal">
                {field.placeholder || `Enter ${field.name.toLowerCase()}`}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

function getColorForType(type: string): string {
  const colors: Record<string, string> = {
    Extraction: "#3b82f6",
    Transformation: "#10b981",
    Loading: "#f59e0b",
    Analysis: "#8b5cf6",
    General: "#6b7280",
  };
  return colors[type] || "#6b7280";
}
