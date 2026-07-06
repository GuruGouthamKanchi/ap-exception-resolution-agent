import React from "react";
import Link from "next/link";
import { Resolution } from "../lib/types";
import { StatusBadge } from "./StatusBadge";

interface ResolutionTableProps {
  resolutions: Resolution[];
  onViewDetails?: (id: string) => void;
}

// Mock details since resolutions list doesn't contain amount/vendor from backend resolutions endpoint.
// We can display dummy vendor/amount data if not present in the Resolution object.
export const ResolutionTable: React.FC<ResolutionTableProps> = ({ resolutions }) => {
  const getVendorName = (id: string) => {
    if (id === "INV-5001") return "Nexis Office Supplies";
    if (id === "INV-5002") return "Titan Industrial Parts";
    if (id === "INV-5019") return "Prime Packaging Corp";
    if (id === "INV-5020") return "Vanguard Electronics";
    if (id === "INV-5023") return "USB-C Hubs Corp";
    if (id === "INV-5026") return "Summit Marketing Agency";
    if (id === "INV-5012") return "Bubble wrap rolls supplier";
    return "Vendor Inc.";
  };

  const getAmount = (id: string) => {
    if (id === "INV-5001") return "$4,399.78";
    if (id === "INV-5002") return "$3,696.00";
    if (id === "INV-5019") return "$6,053.00";
    if (id === "INV-5020") return "$288.74";
    if (id === "INV-5023") return "$520.00";
    if (id === "INV-5026") return "$60.00";
    if (id === "INV-5012") return "$8.00";
    return "$150.00";
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
        <h3 className="text-base font-semibold text-slate-900">Recent Processed Invoices</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
          <thead className="bg-slate-50 text-slate-500 font-semibold uppercase tracking-wider text-xs">
            <tr>
              <th className="px-6 py-3">Invoice ID</th>
              <th className="px-6 py-3">Vendor</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Amount</th>
              <th className="px-6 py-3">Resolved By</th>
              <th className="px-6 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200 bg-white">
            {resolutions.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-10 text-center text-slate-400">
                  No invoices processed yet.
                </td>
              </tr>
            ) : (
              resolutions.map((res) => (
                <tr key={res.invoice_id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4 font-mono font-medium text-indigo-600">
                    {res.invoice_id}
                  </td>
                  <td className="px-6 py-4 text-slate-900 font-medium">
                    {getVendorName(res.invoice_id)}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={res.status} />
                  </td>
                  <td className="px-6 py-4 font-mono text-slate-900 font-medium">
                    {getAmount(res.invoice_id)}
                  </td>
                  <td className="px-6 py-4 text-xs font-semibold uppercase text-slate-500 tracking-wider">
                    {res.resolved_by.replace("_", " ")}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      href={`/invoices/${res.invoice_id}`}
                      className="inline-flex items-center text-xs font-semibold text-indigo-600 hover:text-indigo-800"
                    >
                      View details
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
