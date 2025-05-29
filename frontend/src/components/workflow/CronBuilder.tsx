"use client";

import { useState, useMemo, useRef, useEffect } from "react";

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
  const [minuteSelections, setMinuteSelections] = useState<string[]>([]);
  const [hourSelections, setHourSelections] = useState<string[]>([]);
  const [dayOfMonthSelections, setDayOfMonthSelections] = useState<string[]>([]);
  const [monthSelections, setMonthSelections] = useState<string[]>([]);
  const [dayOfWeekSelections, setDayOfWeekSelections] = useState<string[]>([]);

  const buildCronValue = (selections: string[], allOptions: (string | number)[]) => {
    if (selections.length === 0) return "*";
    if (selections.length === allOptions.length) return "*";
    
    const numericSelections = selections.map(s => {
      if (typeof s === 'string' && isNaN(Number(s))) {
        const index = allOptions.indexOf(s);
        if (allOptions === ranges.month) {
          return index + 1; // Months are 1-12 in cron
        } else if (allOptions === ranges.dayOfMonth) {
          return index + 1; // Days start at 1
        } else {
          return index; // Minutes, hours, days of week start at 0
        }
      }
      return Number(s);
    }).sort((a, b) => a - b);
    
    // Check for ranges
    const ranges_found = [];
    let start = numericSelections[0];
    let end = start;
    
    for (let i = 1; i < numericSelections.length; i++) {
      if (numericSelections[i] === end + 1) {
        end = numericSelections[i];
      } else {
        if (end > start + 1) {
          ranges_found.push(`${start}-${end}`);
        } else if (end === start + 1) {
          ranges_found.push(start.toString(), end.toString());
        } else {
          ranges_found.push(start.toString());
        }
        start = numericSelections[i];
        end = start;
      }
    }
    
    // Handle the last range
    if (end > start + 1) {
      ranges_found.push(`${start}-${end}`);
    } else if (end === start + 1) {
      ranges_found.push(start.toString(), end.toString());
    } else {
      ranges_found.push(start.toString());
    }
    
    return ranges_found.join(",");
  };

  const cronExpression = useMemo(() => {
    const minute = buildCronValue(minuteSelections, ranges.minute);
    const hour = buildCronValue(hourSelections, ranges.hour);
    const dayOfMonth = buildCronValue(dayOfMonthSelections, ranges.dayOfMonth);
    const month = buildCronValue(monthSelections, ranges.month);
    const dayOfWeek = buildCronValue(dayOfWeekSelections, ranges.dayOfWeek);
    
    return `${minute} ${hour} ${dayOfMonth} ${month} ${dayOfWeek}`;
  }, [minuteSelections, hourSelections, dayOfMonthSelections, monthSelections, dayOfWeekSelections]);

  const getDisplayValue = (selections: string[], label: string) => {
    if (selections.length === 0) return `Every ${label.toLowerCase()}`;
    if (selections.length <= 3) return selections.join(", ");
    return `${selections.slice(0, 2).join(", ")}, +${selections.length - 2} more`;
  };

  return (
    <div className="border-base-300 space-y-4">      
      <div className="grid grid-cols gap-2">
        <Select
          label="Minute"
          value={getDisplayValue(minuteSelections, "Minute")}
          selections={minuteSelections}
          setSelections={setMinuteSelections}
          options={ranges.minute}
        />
        <Select
          label="Hour"
          value={getDisplayValue(hourSelections, "Hour")}
          selections={hourSelections}
          setSelections={setHourSelections}
          options={ranges.hour}
        />
        <Select
          label="Day of Month"
          value={getDisplayValue(dayOfMonthSelections, "Day")}
          selections={dayOfMonthSelections}
          setSelections={setDayOfMonthSelections}
          options={ranges.dayOfMonth}
        />
        <Select
          label="Month"
          value={getDisplayValue(monthSelections, "Month")}
          selections={monthSelections}
          setSelections={setMonthSelections}
          options={ranges.month}
        />
        <Select
          label="Day of Week"
          value={getDisplayValue(dayOfWeekSelections, "Day of Week")}
          selections={dayOfWeekSelections}
          setSelections={setDayOfWeekSelections}
          options={ranges.dayOfWeek}
        />
      </div>

      <div className="text-sm text-gray-500 text-right">
        <a
          href={`https://crontab.guru/#${cronExpression.replace(/ /g, "_")}`}
          target="_blank"
          className="link link-accent"
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
  selections,
  setSelections,
  options,
}: {
  label: string;
  value: string;
  selections: string[];
  setSelections: (selections: string[]) => void;
  options: (string | number)[];
}) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleOptionClick = (optionValue: string, event: React.MouseEvent) => {
    event.preventDefault();
    const newSelections = selections.includes(optionValue)
      ? selections.filter(s => s !== optionValue)
      : [...selections, optionValue];
    setSelections(newSelections);
  };

  return (
    <label className="form-control w-full">
      <div className="label">
        <span className="label-text">{label}</span>
      </div>
      <div className="relative" ref={dropdownRef}>
        <div
          className="input input-bordered cursor-pointer flex items-center justify-between min-h-12"
          onClick={() => setIsOpen(!isOpen)}
        >
          <span className={selections.length === 0 ? "text-gray-500" : ""}>{value}</span>
          <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        
        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-base-100 border border-base-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            <div className="p-2">
              <div className="flex items-center gap-2 p-2 hover:bg-base-200 rounded cursor-pointer"
                   onClick={(e) => {
                     e.stopPropagation();
                     setSelections([]);
                   }}>
                <input
                  type="checkbox"
                  className="checkbox checkbox-sm"
                  checked={selections.length === 0}
                  onChange={() => {}}
                  onClick={(e) => e.stopPropagation()}
                />
                <span>All (any value)</span>
              </div>
              {options.map((opt) => (
                <div
                  key={opt}
                  className="flex items-center gap-2 p-2 hover:bg-base-200 rounded cursor-pointer"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOptionClick(opt.toString(), e);
                  }}
                >
                  <input
                    type="checkbox"
                    className="checkbox checkbox-sm"
                    checked={selections.includes(opt.toString())}
                    onChange={() => {}}
                    onClick={(e) => e.stopPropagation()}
                  />
                  <span>{opt}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </label>
  );
}
