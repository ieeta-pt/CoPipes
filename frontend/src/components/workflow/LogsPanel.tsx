interface LogsPanelProps {
  output: string;
}

export function LogsPanel({ output }: LogsPanelProps) {
  return (
    <aside className="w-[calc(30%-2rem)] flex flex-col">
      <div className="flex-1">
        <div className="p-2 mb-4">
          <h1 className="font-semibold">Compilation logs</h1>
        </div>
        <textarea
          className="textarea textarea-bordered border-base-200 w-full h-[calc(90%-2rem)]"
          placeholder="Compilation logs will appear here."
          value={output}
          readOnly
        ></textarea>
      </div>
    </aside>
  );
}
