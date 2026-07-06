"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { AppShell } from "../../../components/AppShell";
import { StatusBadge } from "../../../components/StatusBadge";
import { PipelineTimeline } from "../../../components/PipelineTimeline";
import { DiscrepancyPanel } from "../../../components/DiscrepancyPanel";
import { ReasoningPanel } from "../../../components/ReasoningPanel";
import { Resolution, MatchDiscrepancy, Invoice, MatchResult } from "../../../lib/types";
import { getResolution, getInvoice, getMatchResult } from "../../../lib/api";
import { ArrowLeft, UserCheck, HelpCircle, FileCheck, Loader2, AlertCircle } from "lucide-react";

export default function InvoiceDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [resolution, setResolution] = useState<Resolution | null>(null);
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAllData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Fetch all three datasets in parallel
        const [resolutionData, invoiceData, matchResultData] = await Promise.all([
          getResolution(id),
          getInvoice(id).catch(() => null),
          getMatchResult(id).catch(() => null),
        ]);

        if (!resolutionData) {
          setError(`Invoice resolution for ID ${id} not found.`);
        } else {
          setResolution(resolutionData);
          setInvoice(invoiceData);
          setMatchResult(matchResultData);
        }
      } catch (err: any) {
        console.error(err);
        setError("Failed to fetch resolution details from the backend.");
      } finally {
        setLoading(false);
      }
    };

    if (id) {
      loadAllData();
    }
  }, [id]);

  if (loading) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center p-24 space-y-4">
          <Loader2 className="w-8 h-8 text-indigo-650 animate-spin" />
          <p className="text-sm text-slate-500 font-medium">Loading Invoice Audits...</p>
        </div>
      </AppShell>
    );
  }

  if (error || !resolution) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center p-12 bg-white rounded-lg border border-slate-200 space-y-4 max-w-xl mx-auto mt-12">
          <AlertCircle className="w-12 h-12 text-rose-500" />
          <h3 className="text-lg font-bold text-slate-900">Auditing Error</h3>
          <p className="text-sm text-slate-500 text-center">{error || "Failed to load audit records."}</p>
          <Link
            href="/"
            className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded text-sm font-semibold transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      </AppShell>
    );
  }

  // Dynamic values with clean fallbacks
  const vendorName = invoice?.vendor_name || "Unknown Vendor";
  const invoiceAmount = invoice?.total_amount || 0.0;
  const poNumber = invoice?.po_number || matchResult?.po_number || "N/A";
  const discrepancies: MatchDiscrepancy[] = matchResult?.discrepancies || [];

  const timelineStages = [
    {
      name: "Extraction Stage",
      status: "success" as const,
      description: `Extraction Successful. Extracted vendor "${vendorName}", PO Ref "${poNumber}", total amount $${invoiceAmount.toFixed(2)}, and ${invoice?.line_items?.length || 0} line items.`,
    },
    {
      name: "Matching Stage",
      status: resolution.status === "auto_resolved" ? ("success" as const) : ("warning" as const),
      description:
        resolution.status === "auto_resolved"
          ? `3-Way Match Successful. Invoice values align with Purchase Order ${poNumber}.`
          : `3-Way Match Failed. Discrepancies detected against Purchase Order ${poNumber}. See discrepancy panel for details.`,
    },
    {
      name: "Investigation Stage",
      status: "success" as const,
      description:
        resolution.status === "auto_resolved"
          ? "Policy check completed. Approved for auto-resolution without escalation."
          : `AI Investigation Completed. Decision: Escalated to human review.`,
    },
  ];

  return (
    <AppShell>
      {/* Back to dashboard */}
      <Link
        href="/"
        className="inline-flex items-center text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5 mr-1" />
        Back to Dashboard
      </Link>

      {/* Invoice Header */}
      <div className="bg-white rounded-lg border border-slate-200 p-6 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <h2 className="text-xl font-bold font-mono text-slate-900">
              {resolution.invoice_id}
            </h2>
            <StatusBadge status={resolution.status} />
          </div>
          <p className="text-sm text-slate-500 font-medium">
            Vendor: <span className="text-slate-800">{vendorName}</span> | PO Ref:{" "}
            <span className="font-mono text-slate-800">{poNumber}</span>
          </p>
        </div>
        <div className="flex flex-col items-start md:items-end justify-center">
          <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
            Invoice Amount
          </p>
          <p className="text-2xl font-bold font-mono text-slate-900">
            ${invoiceAmount.toFixed(2)}{" "}
            <span className="text-xs font-medium text-slate-500">USD</span>
          </p>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left Column: Timeline & Discrepancies */}
        <div className="lg:col-span-2 space-y-8">
          <PipelineTimeline stages={timelineStages} />
          <DiscrepancyPanel discrepancies={discrepancies} />
        </div>

        {/* Right Column: Reasoning & Actions */}
        <div className="space-y-8">
          <ReasoningPanel resolution={resolution} />

          {/* Action Cards */}
          <div className="bg-white rounded-lg border border-slate-200 p-6 space-y-3">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">
              Available Actions
            </h4>
            <button className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors">
              <UserCheck className="w-4 h-4" />
              <span>Escalate to Manager</span>
            </button>
            <button className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded text-sm font-semibold text-indigo-650 bg-white border border-indigo-200 hover:bg-slate-50 transition-colors">
              <HelpCircle className="w-4 h-4" />
              <span>Request Vendor Clar.</span>
            </button>
            <button className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 rounded text-sm font-semibold text-slate-650 hover:text-slate-900 transition-colors">
              <FileCheck className="w-4 h-4" />
              <span>Auto-approve with Note</span>
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

