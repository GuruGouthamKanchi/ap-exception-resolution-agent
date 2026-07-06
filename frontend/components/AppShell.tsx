import React from "react";
import Link from "next/link";
import { LayoutDashboard, UploadCloud, Receipt, ShieldAlert } from "lucide-react";

interface AppShellProps {
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ children }) => {
  return (
    <div className="flex h-screen bg-slate-50 text-slate-800 antialiased font-sans">
      {/* Sidebar Navigation */}
      <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col justify-between border-r border-slate-800">
        <div>
          {/* Header/Logo */}
          <div className="px-6 py-5 border-b border-slate-800 flex items-center space-x-3">
            <div className="bg-indigo-600 p-1.5 rounded text-white">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-sm font-bold text-white tracking-tight uppercase">
                AP Exception Agent
              </h1>
              <p className="text-[10px] text-slate-500 font-medium">Internal Auditing System</p>
            </div>
          </div>
          
          {/* Nav Items */}
          <nav className="px-4 py-6 space-y-1">
            <Link
              href="/"
              className="flex items-center space-x-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-slate-800 hover:text-white"
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Overview Dashboard</span>
            </Link>
            <Link
              href="/process"
              className="flex items-center space-x-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors hover:bg-slate-800 hover:text-white"
            >
              <UploadCloud className="w-4 h-4" />
              <span>Process Invoice</span>
            </Link>
          </nav>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-800 text-[10px] text-slate-600">
          AP Exception Agent v1.0.0
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-between px-8 z-10">
          <div className="flex items-center space-x-4">
            <span className="text-xs font-semibold text-slate-400">Environment: Staging</span>
            <span className="h-4 w-px bg-slate-200"></span>
            <span className="text-xs font-semibold text-emerald-600 flex items-center">
              <span className="h-1.5 w-1.5 bg-emerald-500 rounded-full mr-1.5 animate-pulse"></span>
              Live Client Connected
            </span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-semibold text-slate-600 border border-slate-200">
              FO
            </div>
            <span className="text-xs font-semibold text-slate-700">Finance Ops</span>
          </div>
        </header>

        {/* Content Body */}
        <main className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto space-y-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
};
export default AppShell;
