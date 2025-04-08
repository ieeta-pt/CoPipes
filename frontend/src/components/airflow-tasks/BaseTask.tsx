// BaseTask.tsx
import React from "react";
import { TaskConfig, ConfigField } from "./types";

interface BaseTaskProps {
  config: TaskConfig;
  onUpdate: (newConfig: TaskConfig) => void;
}

async function handleFileUpload(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    console.error("Upload failed");
  }
}

export const BaseTask: React.FC<BaseTaskProps> = ({ config, onUpdate }) => {
  const handleChange = (index: number, value: string) => {
    const updated = [...config];
    updated[index].value = value;
    onUpdate(updated);
  };

  return (
    <div className="space-y-2">
      {config.map((field, index) => (
        <div key={field.name}>
          <label className="block text-sm font-medium">{field.name}</label>

          {field.type === "file" ? (
            <input
              type="file"
              className="file-input w-full"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  handleFileUpload(file);
                  handleChange(index, file.name); // store just the filename in config
                }
              }}
            />
          ) : (
            <input
              type="text"
              className="input input-sm input-bordered w-full"
              value={field.value}
              onChange={(e) => handleChange(index, e.target.value)}
            />
          )}
        </div>
      ))}
    </div>
  );
};
