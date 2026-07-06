import React from "react";

interface SummaryCardProps {
  title: string;
  value: string | number;
  highlight?: boolean;
  leftBorderColor?: string;
  icon?: React.ReactNode;
}

export const SummaryCard: React.FC<SummaryCardProps> = ({
  title,
  value,
  highlight = false,
  leftBorderColor = "border-slate-300",
  icon,
}) => {
  return (
    <div
      className={`bg-white rounded-lg border border-slate-200 p-6 flex items-start justify-between relative overflow-hidden transition-all duration-200 hover:shadow-[0_2px_4px_rgba(15,23,42,0.05)] border-l-4 ${leftBorderColor}`}
    >
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </p>
        <p
          className={`font-bold tracking-tight text-slate-900 ${
            highlight ? "text-3xl text-indigo-700" : "text-2xl"
          }`}
        >
          {value}
        </p>
      </div>
      {icon && <div className="text-slate-400 p-1.5 bg-slate-50 rounded">{icon}</div>}
    </div>
  );
};
