"use client";

import React, { useState } from "react";
import { AppShell } from "../../components/AppShell";
import { PipelineTimeline } from "../../components/PipelineTimeline";
import { StatusBadge } from "../../components/StatusBadge";
import { DiscrepancyPanel } from "../../components/DiscrepancyPanel";
import { ReasoningPanel } from "../../components/ReasoningPanel";
import { processInvoice } from "../../lib/api";
import { PipelineSummary } from "../../lib/types";
import { Play, Sparkles, DollarSign, Clock, ShieldAlert, AlertTriangle, FileText } from "lucide-react";

export default function ProcessInvoicePage() {
  const [rawText, setRawText] = useState("");
  const [poNumber, setPoNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PipelineSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Sample Invoice Options
  const samples = [
    {
      label: "INV-5001 (Clean Match)",
      po: "PO-1001",
      text: "INVOICE: #INV-5001\nVendor: Nexis Office Supplies\nDate: 02-Jul-2026\nP.O. NO: PO-1001\n\nItems purchased:\n* Ergonomic chairs -- 22.0 units x $199.99 = 4,399.78 USD\n\nTotal Amount  \nDue: USD 4,399.78\nCurrency: USD\nPlease remit payment within 30 days.",
    },
    {
      label: "INV-5019 (Minor Variance)",
      po: "PO-1019",
      text: "INVOICE: #INV-5019\nVendor: Prime Packaging Corp\nDate: 07/01/2026\nP.O. NO: PO-1019\n\nItems purchased:\n* Ergonomic chairs -- 15.0 units x $200.00 = $3,000.00\n* Whiteboards -- 34.0 units x $85.00 = $2,890.00\n* Copy paper cases -- 5.0 units x USD 32.50 = $162.50\n\nTotal Amount Due: $6,053.00\nCurrency: USD\nPlease remit payment within 30 days.",
    },
    {
      label: "INV-5026 (Major Mismatch)",
      po: "PO-1025",
      text: "=== SUMMIT MARKETING AGENCY ===\nInvoice Ref: INV-5026\nDate: July 05, 2026\nPO Number: PO-1025\n\nDescription                      Qty      Unit Price     Total\n--------------------------------------------------------------\nSteel bolts pack                 5.0       12.00 USD       USD 60.00\n\nTotal Amount  \nDue: USD 60.00\nCurrency: USD\nPlease remit payment within 30 days.",
    },
  ];

  const fillSample = (idx: number) => {
    const selected = samples[idx];
    setRawText(selected.text);
    setPoNumber(selected.po);
  };

  const handleProcess = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rawText.trim() || !poNumber.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const pipelineRes = await processInvoice(rawText.trim(), poNumber.trim());
      setResult(pipelineRes);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Pipeline execution failed. Please verify raw invoice and PO references.");
    } finally {
      setLoading(false);
    }
  };

  // Build dynamic pipeline stage tracking
  const getTimelineStages = () => {
    if (!result) return [];
    
    const extractionSuccess = !result.stage_failed || result.stage_failed !== "extraction";
    const matchingSuccess = extractionSuccess && (!result.stage_failed || result.stage_failed !== "matching");
    const investigationSuccess = matchingSuccess && (!result.stage_failed || result.stage_failed !== "investigation");

    return [
      {
        name: "Extraction Agent",
        status: extractionSuccess ? ("success" as const) : ("failed" as const),
        description: extractionSuccess
          ? `Extraction Successful. Identified Invoice ID: ${result.invoice_id || "Unknown"}`
          : `Extraction Failed: ${result.error || "Unexpected extraction error"}`,
      },
      {
        name: "Matcher Agent",
        status: !extractionSuccess
          ? ("pending" as const)
          : matchingSuccess
          ? ("success" as const)
          : ("failed" as const),
        description: !extractionSuccess
          ? "Waiting for extraction..."
          : matchingSuccess
          ? `3-Way Match Check Completed. Match: ${result.match_result?.is_match ? "Exact" : "Exceptions Found"}.`
          : `Matching Failed: ${result.error || "Unexpected matching logic failure"}`,
      },
      {
        name: "Investigator Agent",
        status: !matchingSuccess
          ? ("pending" as const)
          : investigationSuccess
          ? ("success" as const)
          : ("failed" as const),
        description: !matchingSuccess
          ? "Waiting for match verification..."
          : investigationSuccess
          ? `AI Investigation Completed. Decision: ${result.resolution?.status === "auto_resolved" ? "Auto-resolved by policy" : "Escalated to human review"}.`
          : `Investigation Failed: ${result.error || "Unexpected agent exception"}`,
      },
    ];
  };

  const stages = getTimelineStages();

  return (
    <AppShell>
      <div className="space-y-1">
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          Upload & Process Invoice
        </h2>
        <p className="text-sm text-slate-500">
          Simulate the multi-agent pipeline by pasting raw invoice text and associating a Purchase Order number.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        {/* Left Column: Form */}
        <div className="space-y-6">
          <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-semibold text-slate-900 flex items-center">
                <Sparkles className="w-4 h-4 text-teal-600 mr-2" />
                Invoice Processor Console
              </h3>
              
              {/* Sample loader */}
              <div className="flex items-center space-x-1.5">
                <span className="text-[10px] font-bold text-slate-400 uppercase">Pre-fill:</span>
                <select
                  onChange={(e) => {
                    if (e.target.value !== "") fillSample(Number(e.target.value));
                  }}
                  defaultValue=""
                  className="px-2 py-1 bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-650 rounded hover:bg-slate-100 cursor-pointer"
                >
                  <option value="" disabled>Select Sample</option>
                  {samples.map((s, idx) => (
                    <option key={idx} value={idx}>{s.label}</option>
                  ))}
                </select>
              </div>
            </div>

            <form onSubmit={handleProcess} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-505 uppercase tracking-wider">
                  Raw Invoice Text (OCR Simulation)
                </label>
                <textarea
                  value={rawText}
                  onChange={(e) => setRawText(e.target.value)}
                  rows={8}
                  className="w-full px-3 py-2 border border-slate-350 rounded text-sm bg-slate-50 focus:bg-white focus:ring-2 focus:ring-teal-500 focus:border-teal-500 font-mono text-xs leading-relaxed"
                  placeholder="Paste invoice raw OCR string here..."
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-bold text-slate-550 uppercase tracking-wider">
                  Associated PO Number
                </label>
                <input
                  type="text"
                  value={poNumber}
                  onChange={(e) => setPoNumber(e.target.value)}
                  className="w-full px-3 py-2 border border-slate-355 rounded text-sm bg-slate-50 focus:bg-white focus:ring-2 focus:ring-teal-500 focus:border-teal-500 font-mono"
                  placeholder="e.g. PO-1001"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className={`w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded text-sm font-semibold text-white bg-teal-655 hover:bg-teal-700 transition-colors ${
                  loading ? "opacity-50 cursor-not-allowed animate-pulse" : ""
                }`}
              >
                <Play className="w-4 h-4" />
                <span>{loading ? "Processing Pipeline (10-20s)..." : "Process Invoice"}</span>
              </button>
            </form>
          </div>
        </div>

        {/* Right Column: Progress */}
        <div className="space-y-8">
          {error && (
            <div className="p-4 bg-rose-50 border border-rose-100 rounded text-rose-950 flex items-start space-x-3 text-xs leading-normal">
              <AlertTriangle className="w-5 h-5 text-rose-600 mt-0.5 flex-shrink-0" />
              <div>
                <span className="font-semibold block mb-0.5">Pipeline Execution Failed</span>
                {error}
              </div>
            </div>
          )}

          {loading && (
            <div className="bg-white rounded-lg border border-slate-200 p-12 text-center text-slate-400 flex flex-col items-center justify-center space-y-3">
              <div className="w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-sm font-medium text-slate-600">Running multi-agent pipeline logs...</p>
              <p className="text-xs text-slate-400 max-w-xs">
                Analyzing invoice data, validating PO matching, and executing AI investigations. This may take up to 20 seconds.
              </p>
            </div>
          )}

          {result && !loading && (
            <div className="space-y-8 animate-fadeIn">
              <PipelineTimeline stages={stages} />

              {result.match_result && (
                <DiscrepancyPanel discrepancies={result.match_result.discrepancies} />
              )}

              {/* Final Resolution Summary */}
              {result.resolution && (
                <ReasoningPanel resolution={result.resolution} />
              )}
            </div>
          )}

          {!result && !loading && !error && (
            <div className="bg-white rounded-lg border border-slate-200 p-12 text-center text-slate-400 flex flex-col items-center justify-center space-y-3">
              <ShieldAlert className="w-12 h-12 text-slate-300" />
              <p className="text-sm font-medium">Pipeline Logs & Output will appear here after processing.</p>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
