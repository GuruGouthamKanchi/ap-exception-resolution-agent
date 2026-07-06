"use client";

import React, { useState, useEffect } from "react";
import { AppShell } from "../components/AppShell";
import { SummaryCard } from "../components/SummaryCard";
import { ResolutionTable } from "../components/ResolutionTable";
import { Resolution, DashboardSummary } from "../lib/types";
import { getDashboardSummary, getResolutions } from "../lib/api";
import { BarChart, Wallet, Hourglass, Percent, RefreshCw, AlertCircle } from "lucide-react";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [resolutions, setResolutions] = useState<Resolution[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async () => {
    try {
      setError(null);
      const [summaryData, resolutionsData] = await Promise.all([
        getDashboardSummary(),
        getResolutions(),
      ]);
      setSummary(summaryData);
      // Sort resolutions: most recent first (based on ID or order, we can reverse the list)
      setResolutions([...resolutionsData].reverse());
    } catch (err: any) {
      console.error(err);
      setError("Could not connect to backend — is the FastAPI server running?");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <AppShell>
        <div className="space-y-4 animate-pulse">
          <div className="h-8 bg-slate-200 rounded w-1/3"></div>
          <div className="h-4 bg-slate-200 rounded w-1/2"></div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 pt-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-slate-200 rounded-lg"></div>
            ))}
          </div>
          <div className="h-48 bg-slate-200 rounded-lg"></div>
          <div className="h-64 bg-slate-200 rounded-lg"></div>
        </div>
      </AppShell>
    );
  }

  if (error) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center p-12 bg-white rounded-lg border border-slate-200 space-y-4 max-w-xl mx-auto mt-12">
          <AlertCircle className="w-12 h-12 text-rose-500" />
          <h3 className="text-lg font-bold text-slate-900">Connection Failed</h3>
          <p className="text-sm text-slate-500 text-center">{error}</p>
          <button
            onClick={handleRefresh}
            className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-750 text-white rounded text-sm font-semibold transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Try Again</span>
          </button>
        </div>
      </AppShell>
    );
  }

  // Calculate Rates
  const total = summary?.total_processed || 0;
  const autoResolved = summary?.status_counts?.auto_resolved || 0;
  const autoResolutionRate = total > 0 ? ((autoResolved / total) * 100).toFixed(1) : "0.0";

  return (
    <AppShell>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-bold tracking-tight text-slate-900">
            AP Exception Resolution Agent - Dashboard
          </h2>
          <p className="text-sm text-slate-500">
            Real-time overview of automated invoice processing and resolution metrics.
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center space-x-2 px-3 py-1.5 border border-slate-200 rounded-md text-xs font-semibold text-slate-650 hover:bg-slate-50 hover:text-slate-900 transition-colors bg-white"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} />
          <span>{refreshing ? "Refreshing..." : "Refresh"}</span>
        </button>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <SummaryCard
          title="Total Invoices Processed"
          value={total}
          leftBorderColor="border-blue-500"
          icon={<BarChart className="w-5 h-5 text-blue-500" />}
        />
        <SummaryCard
          title="Total Cost Saved"
          value={`$${(summary?.total_cost_saved_usd || 0).toFixed(2)}`}
          leftBorderColor="border-emerald-500"
          icon={<Wallet className="w-5 h-5 text-emerald-500" />}
        />
        <SummaryCard
          title="Total Time Saved"
          value={`${summary?.total_time_saved_hours || 0} Hours`}
          leftBorderColor="border-sky-500"
          icon={<Hourglass className="w-5 h-5 text-sky-500" />}
        />
        <SummaryCard
          title="Auto-Resolution Rate"
          value={`${autoResolutionRate}%`}
          highlight
          leftBorderColor="border-indigo-600"
          icon={<Percent className="w-5 h-5 text-indigo-600" />}
        />
      </div>

      {/* Chart Breakdown Section */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
        <h3 className="text-base font-semibold text-slate-900 border-b border-slate-100 pb-3">
          Resolution Status Breakdown
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-50 p-4 rounded border border-slate-150 flex flex-col justify-between">
            <span className="text-xs font-semibold text-slate-505 uppercase tracking-wider">
              Auto-Resolved via Policy
            </span>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-slate-800">
                {summary?.resolved_by_counts?.policy_rule || 0}
              </span>
              <span className="text-xs text-slate-500">
                ({total > 0 ? (( (summary?.resolved_by_counts?.policy_rule || 0) / total) * 100).toFixed(1) : "0.0"}%)
              </span>
            </div>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-3 overflow-hidden">
              <div
                className="bg-emerald-500 h-full rounded-full"
                style={{ width: `${total > 0 ? ((summary?.resolved_by_counts?.policy_rule || 0) / total) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
          <div className="bg-slate-50 p-4 rounded border border-slate-150 flex flex-col justify-between">
            <span className="text-xs font-semibold text-slate-505 uppercase tracking-wider">
              Auto-Resolved via AI
            </span>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-slate-800">
                {summary?.resolved_by_counts?.gemini_investigation || 0}
              </span>
              <span className="text-xs text-slate-500">
                ({total > 0 ? (( (summary?.resolved_by_counts?.gemini_investigation || 0) / total) * 100).toFixed(1) : "0.0"}%)
              </span>
            </div>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-3 overflow-hidden">
              <div
                className="bg-teal-500 h-full rounded-full"
                style={{ width: `${total > 0 ? ((summary?.resolved_by_counts?.gemini_investigation || 0) / total) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
          <div className="bg-slate-50 p-4 rounded border border-slate-150 flex flex-col justify-between">
            <span className="text-xs font-semibold text-slate-505 uppercase tracking-wider">
              Escalated (AI Decided)
            </span>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-slate-800">
                {summary?.status_counts?.escalated || 0}
              </span>
              <span className="text-xs text-slate-500">
                ({total > 0 ? (( (summary?.status_counts?.escalated || 0) / total) * 100).toFixed(1) : "0.0"}%)
              </span>
            </div>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-3 overflow-hidden">
              <div
                className="bg-amber-500 h-full rounded-full"
                style={{ width: `${total > 0 ? ((summary?.status_counts?.escalated || 0) / total) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
          <div className="bg-slate-50 p-4 rounded border border-slate-150 flex flex-col justify-between">
            <span className="text-xs font-semibold text-slate-505 uppercase tracking-wider">
              Manual System Errors
            </span>
            <div className="mt-2 flex items-baseline space-x-2">
              <span className="text-2xl font-bold text-slate-800">
                {summary?.resolved_by_counts?.human_required || 0}
              </span>
              <span className="text-xs text-slate-500">
                ({total > 0 ? (( (summary?.resolved_by_counts?.human_required || 0) / total) * 100).toFixed(1) : "0.0"}%)
              </span>
            </div>
            <div className="w-full bg-slate-200 h-1.5 rounded-full mt-3 overflow-hidden">
              <div
                className="bg-indigo-500 h-full rounded-full"
                style={{ width: `${total > 0 ? ((summary?.resolved_by_counts?.human_required || 0) / total) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Invoices Table */}
      <ResolutionTable resolutions={resolutions} />
    </AppShell>
  );
}
