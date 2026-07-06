import React from "react";
import { BrainCircuit, DollarSign, Clock } from "lucide-react";
import { Resolution } from "../lib/types";

interface ReasoningPanelProps {
  resolution: Resolution;
}

export const ReasoningPanel: React.FC<ReasoningPanelProps> = ({ resolution }) => {
  return (
    <div className="bg-slate-900 text-slate-100 rounded-lg border border-slate-800 p-6 space-y-6 relative overflow-hidden">
      <div className="absolute right-0 top-0 translate-x-4 -translate-y-4 opacity-5 pointer-events-none">
        <BrainCircuit className="w-40 h-40" />
      </div>
      
      <div className="flex items-center space-x-2 border-b border-slate-800 pb-4">
        <BrainCircuit className="w-5 h-5 text-teal-400" />
        <h3 className="text-base font-semibold text-slate-200">
          AI Exception Investigation Reasoning
        </h3>
      </div>

      <div className="space-y-4">
        <p className="text-sm text-slate-300 leading-relaxed font-normal whitespace-pre-line">
          {resolution.reasoning}
        </p>

        <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-2">
          <p className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
            Recommended Action Outcome
          </p>
          <p className="font-mono text-sm font-semibold text-teal-400">
            {resolution.status === "auto_resolved" ? "POLICY APPROVED" : "HUMAN ESCALATION REQUIRED"}
          </p>
          <p className="text-xs text-slate-400">
            Assigned to: <span className="underline">{resolution.resolved_by.replace("_", " ")}</span>
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 pt-2">
          <div className="bg-slate-950/50 p-4 rounded border border-slate-850/50 flex items-center space-x-3">
            <div className="p-2 bg-emerald-500/10 rounded text-emerald-400">
              <DollarSign className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                Cost Saved
              </p>
              <p className="text-sm font-bold text-slate-200">
                ${resolution.estimated_manual_cost.toFixed(2)}
              </p>
            </div>
          </div>
          <div className="bg-slate-950/50 p-4 rounded border border-slate-850/50 flex items-center space-x-3">
            <div className="p-2 bg-sky-500/10 rounded text-sky-400">
              <Clock className="w-4 h-4" />
            </div>
            <div>
              <p className="text-[10px] font-bold text-slate-500 uppercase tracking-wider">
                Time Saved
              </p>
              <p className="text-sm font-bold text-slate-200">
                {resolution.estimated_time_saved_minutes} min
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
