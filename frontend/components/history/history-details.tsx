"use client";

import { FileText, Table2 } from "lucide-react";
import type { HistoryEntry } from "@/types/history";

export function HistoryDetails({ entry }: { entry: HistoryEntry | null }) {
  if (!entry) {
    return null;
  }

  return (
    <div className="space-y-4 rounded-2xl border border-slate-200 p-5 dark:border-slate-800">
      <div>
        <p className="text-sm font-semibold">Dataset metadata</p>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{entry.dataset_name}</p>
      </div>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
          <p className="text-xs uppercase tracking-wide text-slate-400">Scenario</p>
          <p className="mt-1 font-semibold">{entry.scenario}</p>
        </div>
        <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
          <p className="text-xs uppercase tracking-wide text-slate-400">Quality</p>
          <p className="mt-1 font-semibold">{Object.entries(entry.quality).map(([name, value]) => `${name}: ${value}`).join(" · ")}</p>
        </div>
      </div>
      <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
        <div className="flex items-center gap-2">
          <Table2 className="h-4 w-4" />
          <p className="text-sm font-semibold">Table counts</p>
        </div>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">Customers: {entry.customers.toLocaleString()} · Orders: {entry.orders.toLocaleString()}</p>
      </div>
      <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          <p className="text-sm font-semibold">Preview</p>
        </div>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{entry.readme_preview ?? "No preview available."}</p>
      </div>
    </div>
  );
}
