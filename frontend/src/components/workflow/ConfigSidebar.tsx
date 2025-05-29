import React, { useState } from "react";
import CronBuilder from "./CronBuilder";

export function ConfigSidebar() {
  const [executionType, setExecutionType] = useState("now");

  return (
    <aside 
      className="w-[18rem] bg-base-100 rounded-box shadow-lg border border-base-200 p-4 flex flex-col justify-between h-full"
      data-schedule-type={executionType}
    >
      <div>
      <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
        Schedule Workflow
      </h2>

      {/* Execution Mode Selector */}
      <div className="flex justify-between gap-2 tabs tabs-box mb-4">
        <a
          className={`tab ${
            executionType === "now" ? "tab-active font-bold" : ""
          }`}
          onClick={() => setExecutionType("now")}
        >
          Now
        </a>
        <a
          className={`tab ${
            executionType === "later" ? "tab-active font-bold" : ""
          }`}
          onClick={() => setExecutionType("later")}
        >
          Later
        </a>
        <a
          className={`tab ${
            executionType === "multiple" ? "tab-active font-bold" : ""
          }`}
          onClick={() => setExecutionType("multiple")}
        >
          Multiple
        </a>
      </div>

      {/* Execution Details */}
      {executionType === "later" && (
        <div className="space-y-4 grid grid-cols ">
          <label className="form-control w-full">
            <div className="label">
              <span className="label-text">Execution Date</span>
            </div>
            <input
              type="date"
              className="input input-bordered"
              defaultValue={new Date().toISOString().split("T")[0]}
            />
          </label>
        </div>
      )}

      {executionType === "multiple" && <CronBuilder />}
      </div>
    </aside>
  );
}
