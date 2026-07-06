import React from "react";
import { AlertCircle } from "lucide-react";
import { MatchDiscrepancy } from "../lib/types";

interface DiscrepancyPanelProps {
  discrepancies: MatchDiscrepancy[];
}

export const DiscrepancyPanel: React.FC<DiscrepancyPanelProps> = ({ discrepancies }) => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
      <h3 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3">
        Detected Discrepancies
      </h3>
      {discrepancies.length === 0 ? (
        <div className="flex items-center space-x-2 text-emerald-600 bg-emerald-50/50 p-4 rounded border border-emerald-100 text-sm">
          <span className="font-semibold">Clean Match:</span> No discrepancies detected against Purchase Order or Goods Receipt.
        </div>
      ) : (
        <div className="space-y-3">
          {discrepancies.map((d, idx) => (
            <div
              key={idx}
              className={`p-4 rounded border flex items-start space-x-3 text-sm ${
                d.severity === "major"
                  ? "bg-rose-50/30 border-rose-100 text-rose-900"
                  : "bg-amber-50/30 border-amber-100 text-amber-900"
              }`}
            >
              <AlertCircle
                className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                  d.severity === "major" ? "text-rose-600" : "text-amber-600"
                }`}
              />
              <div className="flex-grow space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold uppercase tracking-wider text-xs text-slate-500">
                    Field: {d.field.replace("_", " ")}
                  </span>
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                      d.severity === "major"
                        ? "bg-rose-100 text-rose-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {d.severity}
                  </span>
                </div>
                <div className="text-xs space-y-0.5">
                  <p>
                    <span className="font-medium text-slate-600">Invoice value:</span>{" "}
                    <span className="font-mono">{d.invoice_value}</span>
                  </p>
                  <p>
                    <span className="font-medium text-slate-600">PO / GR value:</span>{" "}
                    <span className="font-mono">{d.po_value}</span>
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
