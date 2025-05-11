interface LogsPanelProps {
  output: string;
}

export function LogsPanel({ output }: LogsPanelProps) {
  return (
    <aside className="w-[calc(30%-2rem)] p-2 flex flex-col">
      <div className="flex-1">
        <div className="border border-base-200 rounded-sm p-2 mb-4">
          <h2 className="font-semibold mb-2">Compilation logs</h2>
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
