export interface LineItem {
  description: string;
  quantity: number;
  unit_price: number;
  line_total: number;
}

export interface Invoice {
  invoice_id: string;
  vendor_name: string;
  invoice_date: string;
  po_number: string;
  currency: string;
  line_items: LineItem[];
  total_amount: number;
  raw_source: string;
}

export interface PurchaseOrder {
  po_number: string;
  vendor_name: string;
  line_items: LineItem[];
  total_amount: number;
  status: string;
}

export interface GoodsReceipt {
  po_number: string;
  received_items: {
    description: string;
    quantity_received: number;
  }[];
  receipt_date: string;
}

export interface MatchDiscrepancy {
  field: string;
  invoice_value: string;
  po_value: string;
  severity: "minor" | "major";
}

export interface MatchResult {
  invoice_id: string;
  po_number: string;
  is_match: boolean;
  discrepancies: MatchDiscrepancy[];
}

export interface Resolution {
  invoice_id: string;
  status: "auto_resolved" | "escalated";
  reasoning: string;
  resolved_by: "policy_rule" | "gemini_investigation" | "human_required";
  estimated_manual_cost: number;
  estimated_time_saved_minutes: number;
}

export interface DashboardSummary {
  total_processed: number;
  status_counts: {
    auto_resolved: number;
    escalated: number;
  };
  total_cost_saved_usd: number;
  total_time_saved_minutes: number;
  total_time_saved_hours: number;
  resolved_by_counts: {
    policy_rule: number;
    gemini_investigation: number;
    human_required: number;
  };
}

export interface PipelineSummary {
  invoice_id: string | null;
  stage_failed: string | null;
  error?: string | null;
  match_result: MatchResult | null;
  resolution: Resolution | null;
}
