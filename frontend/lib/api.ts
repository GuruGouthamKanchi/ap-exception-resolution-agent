import { DashboardSummary, Resolution, PipelineSummary } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getDashboardSummary(): Promise<DashboardSummary> {
  const res = await fetch(`${API_URL}/dashboard-summary`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch dashboard summary: ${res.statusText}`);
  }
  return res.json();
}

export async function getResolutions(): Promise<Resolution[]> {
  const res = await fetch(`${API_URL}/resolutions`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`Failed to fetch resolutions: ${res.statusText}`);
  }
  return res.json();
}

export async function getResolution(invoiceId: string): Promise<Resolution | null> {
  const res = await fetch(`${API_URL}/resolutions/${invoiceId}`, { cache: "no-store" });
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`Failed to fetch resolution ${invoiceId}: ${res.statusText}`);
  }
  return res.json();
}

export async function getInvoice(invoiceId: string): Promise<any | null> {
  const res = await fetch(`${API_URL}/invoices/${invoiceId}`, { cache: "no-store" });
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`Failed to fetch invoice ${invoiceId}: ${res.statusText}`);
  }
  return res.json();
}

export async function getMatchResult(invoiceId: string): Promise<any | null> {
  const res = await fetch(`${API_URL}/match-results/${invoiceId}`, { cache: "no-store" });
  if (res.status === 404) {
    return null;
  }
  if (!res.ok) {
    throw new Error(`Failed to fetch match result ${invoiceId}: ${res.statusText}`);
  }
  return res.json();
}


export async function processInvoice(rawText: string, poNumber: string): Promise<PipelineSummary> {
  const res = await fetch(`${API_URL}/process-invoice`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      raw_text: rawText,
      po_number: poNumber,
    }),
  });
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Server returned error status ${res.status}`);
  }
  return res.json();
}
