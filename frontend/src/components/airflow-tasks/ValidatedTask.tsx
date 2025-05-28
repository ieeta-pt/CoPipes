import React, { useState, useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { TaskConfig, ConfigField, WorkflowComponent } from "@/components/airflow-tasks/types";

interface ValidatedTaskProps {
  config: TaskConfig;
  onUpdate: (newConfig: TaskConfig) => void;
  availableTasks?: WorkflowComponent[];
  taskId?: string;
}

const createValidationSchema = (config: TaskConfig) => {
  const schemaObject: Record<string, z.ZodTypeAny> = {};
  
  config.forEach((field) => {
    let fieldSchema: z.ZodString = z.string();
    
    if (field.type === "boolean") {
      fieldSchema = z.string().transform(val => val === "true" || val === "True") as any;
    } else if (field.validation?.pattern) {
      fieldSchema = z.string().regex(new RegExp(field.validation.pattern), {
        message: field.validation.message || "Invalid format"
      });
    }
    
    if (field.required) {
      fieldSchema = fieldSchema.min(1, field.validation?.message || `${field.name} is required`);
    } else {
      fieldSchema = fieldSchema.optional() as any;
    }
    
    schemaObject[field.name] = fieldSchema;
  });
  
  return z.object(schemaObject);
};

const transformHumanToAirflow = (value: string, fieldType: string): string => {
  if (fieldType === "select") {
    const transformMap: Record<string, string> = {
      "Comma": ",",
      "Semicolon": ";",
      "Tab": "\t"
    };
    return transformMap[value] || value;
  }
  return value;
};

const transformAirflowToHuman = (value: string, fieldType: string): string => {
  if (fieldType === "select") {
    const transformMap: Record<string, string> = {
      ",": "Comma",
      ";": "Semicolon",
      "\t": "Tab"
    };
    return transformMap[value] || value;
  }
  return value;
};

export const ValidatedTask: React.FC<ValidatedTaskProps> = ({ 
  config, 
  onUpdate, 
  availableTasks = [],
  taskId 
}) => {
  const [editingField, setEditingField] = useState<string | null>(null);
  const [tempValue, setTempValue] = useState<string>("");
  const modalRef = useRef<HTMLDialogElement>(null);
  
  const validationSchema = createValidationSchema(config);
  
  const defaultValues = config.reduce((acc, field) => {
    acc[field.name] = transformAirflowToHuman(field.value, field.type);
    return acc;
  }, {} as Record<string, string>);

  const {
    watch,
    formState: { errors, isValid },
    setValue,
    trigger
  } = useForm({
    resolver: zodResolver(validationSchema),
    defaultValues,
    mode: "onChange"
  });

  const watchedValues = watch();

  React.useEffect(() => {
    if (isValid) {
      const updatedConfig = config.map((field) => ({
        ...field,
        value: transformHumanToAirflow(watchedValues[field.name] || "", field.type)
      }));
      
      // Only update if values actually changed
      const hasChanges = updatedConfig.some((newField, index) => 
        newField.value !== config[index]?.value
      );
      
      if (hasChanges) {
        onUpdate(updatedConfig);
      }
    }
  }, [watchedValues, isValid]);

  const getAvailableTasksForReference = (currentTaskId?: string) => {
    if (!currentTaskId) return availableTasks;
    
    // Find the index of the current task
    const currentIndex = availableTasks.findIndex(task => task.id === currentTaskId);
    
    // Only return tasks that appear before the current task (above in the workflow)
    return availableTasks.slice(0, currentIndex).filter(task => task.id !== currentTaskId);
  };

  const openModal = (fieldName: string, currentValue: string) => {
    setEditingField(fieldName);
    setTempValue(currentValue);
    modalRef.current?.showModal();
  };

  const closeModal = () => {
    setEditingField(null);
    setTempValue("");
    modalRef.current?.close();
  };

  const saveValue = () => {
    if (editingField) {
      setValue(editingField, tempValue);
      trigger(editingField);
    }
    closeModal();
  };

  const getFieldValue = (field: ConfigField) => {
    const currentValue = watchedValues[field.name] || field.value;
    
    switch (field.type) {
      case "file":
        return currentValue ? `📎 ${currentValue}` : "No file selected";
      case "boolean":
        const isChecked = currentValue === "true" || currentValue === "True";
        return isChecked ? "Enabled" : "Disabled";
      case "task_reference":
        if (currentValue && currentValue.startsWith('$ref:')) {
          const availableTasksForRef = getAvailableTasksForReference(taskId);
          const task = availableTasksForRef.find(t => `$ref:${t.id}` === currentValue);
          return task ? `→ ${task.content}` : `Unknown task (${currentValue})`;
        }
        return `Select task`;
      case "select":
        return currentValue || "Select option...";
      default:
        return currentValue || "Click to edit...";
    }
  };

  const handleFieldClick = (field: ConfigField) => {
    const currentValue = watchedValues[field.name] || field.value;
    
    switch (field.type) {
      case "file":
        // Create a file input and trigger it
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.onchange = async (e) => {
          const file = (e.target as HTMLInputElement).files?.[0];
          if (file) {
            try {
              const formData = new FormData();
              formData.append("file", file);
              const res = await fetch("/api/upload", {
                method: "POST",
                body: formData,
              });
              if (res.ok) {
                const result = await res.json();
                setValue(field.name, result.filename || file.name);
              } else {
                setValue(field.name, file.name);
              }
              trigger(field.name);
            } catch (error) {
              console.error("File upload error:", error);
              setValue(field.name, file.name);
              trigger(field.name);
            }
          }
        };
        fileInput.click();
        break;
        
      case "boolean":
        const isCurrentlyChecked = currentValue === "true" || currentValue === "True";
        const newValue = isCurrentlyChecked ? "False" : "True";
        setValue(field.name, newValue);
        trigger(field.name);
        break;
        
      case "select":
        // For select, we'll use a simple modal with options
        setEditingField(field.name);
        setTempValue(currentValue);
        modalRef.current?.showModal();
        break;
        
      case "task_reference":
        // For task reference, we'll use a modal with available tasks
        setEditingField(field.name);
        setTempValue(currentValue);
        modalRef.current?.showModal();
        break;
        
      default:
        // For text inputs, open modal
        openModal(field.name, currentValue);
        break;
    }
  };

  const renderModalContent = () => {
    if (!editingField) return null;
    
    const field = config.find(f => f.name === editingField);
    if (!field) return null;
    
    switch (field.type) {
      case "select":
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">{field.name}</h3>
            <div className="space-y-2">
              {field.options?.map((option) => (
                <button
                  key={option}
                  className={`w-full p-3 text-left border rounded ${
                    tempValue === option ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                  }`}
                  onClick={() => setTempValue(option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        );
        
      case "task_reference":
        const availableTasksForModal = getAvailableTasksForReference(taskId);
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">{field.name}</h3>
            {availableTasksForModal.length === 0 ? (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded text-blue-700">
                Add tasks above this one to reference their outputs
              </div>
            ) : (
              <div className="space-y-2">
                <button
                  className={`w-full p-3 text-left border rounded ${
                    tempValue === "" ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                  }`}
                  onClick={() => setTempValue("")}
                >
                  None selected
                </button>
                {availableTasksForModal.map((task) => (
                  <button
                    key={task.id}
                    className={`w-full p-3 text-left border rounded ${
                      tempValue === `$ref:${task.id}` ? 'border-blue-500 bg-blue-50' : 'border-gray-300'
                    }`}
                    onClick={() => setTempValue(`$ref:${task.id}`)}
                  >
                    <div className="font-medium">{task.content}</div>
                    <div className="text-sm text-gray-500">{task.type} (ID: {task.id})</div>
                  </button>
                ))}
              </div>
            )}
          </div>
        );
        
      default:
        return (
          <div className="space-y-4">
            <h3 className="text-lg font-medium">{field.name}</h3>
            <textarea
              className="textarea textarea-bordered w-full h-32"
              value={tempValue}
              onChange={(e) => setTempValue(e.target.value)}
              placeholder={field.placeholder}
            />
            {field.placeholder && (
              <p className="text-sm text-gray-500">{field.placeholder}</p>
            )}
          </div>
        );
    }
  };

  return (
    <>
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 p-4 bg-base-100 rounded-lg min-w-0">
        {config.map((field) => {
          const fieldError = errors[field.name];
          return (
            <div
              key={field.name}
              className={`flex flex-col p-3 bg-white rounded border shadow-sm cursor-pointer hover:shadow-md transition-shadow ${
                fieldError ? 'border-red-300' : 'border-gray-200'
              }`}
              onClick={() => handleFieldClick(field)}
            >
              <span className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-1">
                {field.name}
                {field.required && <span className="text-red-500 ml-1">*</span>}
              </span>
              <span className="text-sm text-gray-900 whitespace-pre-line break-normal">
                {getFieldValue(field)}
              </span>
              {fieldError && (
                <span className="text-xs text-red-500 mt-1">
                  {fieldError.message as string}
                </span>
              )}
            </div>
          );
        })}
      </div>

      {/* Modal */}
      <dialog ref={modalRef} className="modal">
        <div className="modal-box w-11/12 max-w-2xl">
          {renderModalContent()}
          <div className="modal-action">
            <button className="btn btn-ghost" onClick={closeModal}>
              Cancel
            </button>
            <button className="btn btn-primary" onClick={saveValue}>
              Save
            </button>
          </div>
        </div>
        <form method="dialog" className="modal-backdrop">
          <button onClick={closeModal}>close</button>
        </form>
      </dialog>
    </>
  );
};