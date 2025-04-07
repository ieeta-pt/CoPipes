import { useSortable } from "@dnd-kit/sortable"
import { CSS } from "@dnd-kit/utilities"
import { X, GripVertical } from "lucide-react"
import { WorkflowItem } from "@/components/airflow-tasks/types"
import { Registry } from "@/components/airflow-tasks/Registry"

type Props = {
  item: WorkflowItem
  onRemove: (id: string) => void
  onUpdate: (config: WorkflowItem["config"]) => void
  isOverlay?: boolean
}

export const SortableItem: React.FC<Props> = ({ item, onRemove, onUpdate, isOverlay = false }) => {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: item.id })
  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    borderLeft: `4px solid ${getColorForType(item.type)}`,
    opacity: isOverlay ? 0.8 : 1,
    cursor: isOverlay ? "grabbing" : "default",
    zIndex: isOverlay ? 999 : "auto",
  }

  const TaskComponent = Registry[item.content]?.component

  return (
    <div ref={setNodeRef} style={style} className="card bg-base-100 shadow-md">
      <div className="card-body p-4">
        <div className="flex justify-between items-start mb-2">
          <div className="font-medium">{item.content}</div>
          {!isOverlay && (
            <div className="flex gap-2">
              <button className="btn btn-xs btn-soft btn-secondary cursor-grab" {...listeners} {...attributes}>
                <GripVertical className="h-4 w-4" />
              </button>
              <button className="btn btn-xs btn-error" onClick={() => onRemove(item.id)}>
                <X className="h-4 w-4" />
              </button>
            </div>
          )}
        </div>
        {TaskComponent && (
          <TaskComponent config={item.config} onUpdate={onUpdate} />
        )}
      </div>
    </div>
  )
}

function getColorForType(type: string): string {
  const colors: Record<string, string> = {
    Extraction: "#3b82f6",
    Transformation: "#10b981",
    Loading: "#f59e0b",
    Analysis: "#8b5cf6",
    General: "#6b7280",
  }
  return colors[type] || "#6b7280"
}
