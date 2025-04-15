// import React from "react";
// import { TaskConfig } from "@/components/airflow-tasks/types";

// interface BaseTaskProps {
//   config: TaskConfig;
//   onUpdate: (newConfig: TaskConfig) => void;
// }

// async function handleFileUpload(file: File) {
//   const formData = new FormData();
//   formData.append("file", file);

//   const res = await fetch("/api/upload", {
//     method: "POST",
//     body: formData,
//   });

//   if (!res.ok) {
//     console.error("Upload failed");
//   }
// }

// export const BaseTask: React.FC<BaseTaskProps> = ({ config, onUpdate }) => {
//   const handleChange = (index: number, value: string) => {
//     const updated = [...config];
//     updated[index].value = value;
//     onUpdate(updated);
//   };

//   return (
//     <div className="space-y-2">
//       {config.map((field, index) => (
//         <div key={field.name}>
//           <label className="block text-sm font-medium">{field.name}</label>

//           {field.type === "file" ? (
//             <input
//               type="file"
//               className="file-input w-full"
//               onChange={(e) => {
//                 const file = e.target.files?.[0];
//                 if (file) {
//                   handleFileUpload(file);
//                   handleChange(index, file.name); // store just the filename in config
//                 }
//               }}
//             />
//           ) : (
//             <input
//               type="text"
//               className="input input-sm input-bordered w-full"
//               value={field.value}
//               onChange={(e) => handleChange(index, e.target.value)}
//             />
//           )}
//         </div>
//       ))}
//     </div>
//   );
// };

import React from "react";
import { TaskConfig } from "@/components/airflow-tasks/types";

interface BaseTaskProps {
  config: TaskConfig;
  onUpdate: (newConfig: TaskConfig) => void;
}

export const BaseTask: React.FC<BaseTaskProps> = ({ config }) => {
  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 p-4 bg-base-100 rounded-lg min-w-0">
      {config.map((field) => (
        <div
          key={field.name}
          className="flex flex-col p-3 bg-white rounded border border-gray-200 shadow-sm"
        >
          <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">
            {field.name}
          </span>
          <span className="text-sm text-gray-900 whitespace-pre-line break-normal">
            {field.type === "file"
              ? `📎 ${field.value || "No file uploaded"}`
              : field.value || "-"}
          </span>
        </div>
      ))}
    </div>
  );
};
