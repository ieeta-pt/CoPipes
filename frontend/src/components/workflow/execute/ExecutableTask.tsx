import React from "react";
import { TaskConfig, ConfigField } from "@/components/airflow-tasks/types";
import { showToast } from "@/components/layout/ShowToast";

interface ExecutableTaskProps {
  config: TaskConfig;
  onUpdate: (newConfig: TaskConfig) => void;
  isReadOnly?: boolean;
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
    throw new Error("Upload failed");
  }

  return res.json();
}

export const ExecutableTask: React.FC<ExecutableTaskProps> = ({
  config,
  onUpdate,
}) => {
  const handleChange = (index: number, value: string) => {
    const updated = [...config];
    updated[index].value = value;
    onUpdate(updated);
  };

  const renderField = (field: ConfigField, index: number) => {
    switch (field.type) {
      case "file":
        return (
          <input
            type="file"
            className="file-input file-input-bordered w-full"
            onChange={async (e) => {
              const file = e.target.files?.[0];
              if (file) {
                try {
                  const result = await handleFileUpload(file);
                  handleChange(index, result.filename); // store the filename returned from the server
                } catch (error) {
                  console.error("File upload failed:", error);
                  showToast("File upload failed.", "error");
                }
              }
            }}
          />
        );

      case "boolean":
        const options = ["True", "False"]
        return (
          <div className="flex gap-2">
            {options.map((option, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleChange(index, option)}
                className={`px-4 py-2 rounded-full border transition-colors
        ${
          field.value === option
            ? "bg-primary text-white border-primary"
            : "bg-base-200 text-base-content border-base-300 hover:bg-base-300"
        }`}
              >
                {option}
              </button>
            ))}
          </div>
        );

      case "radio":
        if (!field.options) {
          console.warn(`No options provided for radio field: ${field.name}`);
          showToast(
            `No options provided for radio field: ${field.name}`,
            "warning"
          );
          return null;
        }
        return (
          <div className="flex flex-col gap-2">
            {field.options.map((option, i) => (
              <label key={i} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="radio"
                  name={field.name}
                  className="radio radio-primary"
                  checked={field.value === option}
                  onChange={() => handleChange(index, option)}
                />
                <span className="text-sm">{option}</span>
              </label>
            ))}
          </div>
        );

      case "select":
        if (!field.options) {
          console.warn(`No options provided for select field: ${field.name}`);
          showToast(
            `No options provided for select field: ${field.name}`,
            "warning"
          );
          return null;
        }
        return (
          <select
            className="select select-bordered w-full"
            value={field.value}
            onChange={(e) => handleChange(index, e.target.value)}
          >
            <option value="">Select an option</option>
            {field.options.map((option, i) => (
              <option key={i} value={option}>
                {option}
              </option>
            ))}
          </select>
        );

      case "string":
      default:
        return (
          <input
            type="text"
            className="input input-bordered w-full"
            value={field.value}
            onChange={(e) => handleChange(index, e.target.value)}
            placeholder={`Enter ${field.name.toLowerCase()}`}
          />
        );
    }
  };

  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 p-4 bg-base-100 rounded-lg min-w-0">
      {config.map((field, index) => (
        <div
          key={field.name}
          className="flex flex-col p-3 bg-white rounded border border-gray-200 shadow-sm"
        >
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            {field.name}
          </span>
          {renderField(field, index)}
        </div>
      ))}
    </div>
  );
};
