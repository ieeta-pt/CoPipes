"use client";

import { useState, useMemo } from "react";

const ranges = {
  minute: [...Array(60).keys()],
  hour: [...Array(24).keys()],
  dayOfMonth: [...Array(31).keys()].map((i) => i + 1),
  month: [
    "JAN",
    "FEB",
    "MAR",
    "APR",
    "MAY",
    "JUN",
    "JUL",
    "AUG",
    "SEP",
    "OCT",
    "NOV",
    "DEC",
  ],
  dayOfWeek: ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"],
};

export default function CronBuilder() {
  const [minute, setMinute] = useState("*");
  const [hour, setHour] = useState("*");
  const [dayOfMonth, setDayOfMonth] = useState("*");
  const [month, setMonth] = useState("*");
  const [dayOfWeek, setDayOfWeek] = useState("*");

  const cronExpression = useMemo(
    () => `${minute} ${hour} ${dayOfMonth} ${month} ${dayOfWeek}`,
    [minute, hour, dayOfMonth, month, dayOfWeek]
  );

  return (
    <div className="border-base-300 space-y-4">
      <div className="grid grid-cols gap-2">
        <Select
          label="Minute"
          value={minute}
          setValue={setMinute}
          options={ranges.minute}
        />
        <Select
          label="Hour"
          value={hour}
          setValue={setHour}
          options={ranges.hour}
        />
        <Select
          label="Day of Month"
          value={dayOfMonth}
          setValue={setDayOfMonth}
          options={ranges.dayOfMonth}
        />
        <Select
          label="Month"
          value={month}
          setValue={setMonth}
          options={ranges.month}
        />
        <Select
          label="Day of Week"
          value={dayOfWeek}
          setValue={setDayOfWeek}
          options={ranges.dayOfWeek}
        />
      </div>

      <div className="text-xs text-gray-500 text-right">
        <a
          href={`https://crontab.guru/#${cronExpression.replace(/ /g, "_")}`}
          target="_blank"
          className="link link-primary"
        >
          ↗ Preview on crontab.guru
        </a>
      </div>
    </div>
  );
}

function Select({
  label,
  value,
  setValue,
  options,
}: {
  label: string;
  value: string | number;
  setValue: (v: string) => void;
  options: (string | number)[];
}) {
  return (
    <label className="form-control w-full">
      <div className="label">
        <span className="label-text">{label}</span>
      </div>
      <select
        className="select select-bordered select-md"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      >
        <option value="*">Every {label.toLowerCase()}</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt}
          </option>
        ))}
      </select>
    </label>
  );
}
