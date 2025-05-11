import { TaskMenu } from "@/components/workflow/TaskMenu";

export function Sidebar({ onAddComponent }: { onAddComponent: (content: string) => void }) {
  return (
    <aside className="w-[calc(20%-2rem)] h-[calc(100%-2rem)] bg-base-100 border-base-200 p-2">
        <TaskMenu onAddComponent={onAddComponent} />
    </aside>
  );
}
