import React from "react";
import { CheckCircle2, AlertTriangle, PlayCircle } from "lucide-react";

interface PipelineStage {
  name: string;
  status: "success" | "warning" | "failed" | "pending";
  description: string;
}

interface PipelineTimelineProps {
  stages: PipelineStage[];
}

export const PipelineTimeline: React.FC<PipelineTimelineProps> = ({ stages }) => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-6">
      <h3 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3">
        Pipeline Execution Stages
      </h3>
      <div className="relative border-l border-slate-200 ml-4 pl-6 space-y-8">
        {stages.map((stage, idx) => {
          let Icon = PlayCircle;
          let iconColor = "text-slate-300 bg-white";
          
          if (stage.status === "success") {
            Icon = CheckCircle2;
            iconColor = "text-emerald-600 bg-white";
          } else if (stage.status === "failed" || stage.status === "warning") {
            Icon = AlertTriangle;
            iconColor = "text-amber-500 bg-white";
          }
          
          return (
            <div key={idx} className="relative">
              {/* Timeline dot */}
              <span className="absolute -left-[35px] top-0.5 rounded-full p-0.5">
                <Icon className={`w-5 h-5 ${iconColor}`} />
              </span>
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <h4 className="text-sm font-semibold text-slate-800">{stage.name}</h4>
                  <span
                    className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-sm ${
                      stage.status === "success"
                        ? "bg-emerald-50 text-emerald-700"
                        : stage.status === "failed" || stage.status === "warning"
                        ? "bg-amber-50 text-amber-700"
                        : "bg-slate-100 text-slate-500"
                    }`}
                  >
                    {stage.status}
                  </span>
                </div>
                <p className="text-xs text-slate-500 leading-relaxed">{stage.description}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
