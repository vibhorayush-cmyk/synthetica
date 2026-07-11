"use client";

import { Copy, Download, Eye, RotateCw, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { HistoryEntry } from "@/types/history";

export function HistoryCard({
  entry,
  onView,
  onDownload,
  onRegenerate,
  onClone,
  onDelete,
}: {
  entry: HistoryEntry;
  onView: (entry: HistoryEntry) => void;
  onDownload: (entry: HistoryEntry) => void;
  onRegenerate: (entry: HistoryEntry) => void;
  onClone: (entry: HistoryEntry) => void;
  onDelete: (entry: HistoryEntry) => void;
}) {
  return (
    <Card className="flex h-full flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold">{entry.dataset_name}</h3>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{entry.industry} · {entry.scenario}</p>
        </div>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold dark:bg-slate-800">{entry.status}</span>
      </div>
      <div className="grid gap-3 text-sm text-slate-600 dark:text-slate-400 sm:grid-cols-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Generated</p>
          <p>{new Date(entry.generated_at).toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-slate-400">Duration</p>
          <p>{entry.generation_duration_ms} ms</p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2 text-xs text-slate-500">
        <span className="rounded-full bg-slate-100 px-2.5 py-1 dark:bg-slate-800">{entry.export_type}</span>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 dark:bg-slate-800">{entry.zip_size} bytes</span>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 dark:bg-slate-800">{entry.customers.toLocaleString()} customers</span>
      </div>
      <p className="text-sm text-slate-500">Template: {entry.template_name ?? "Manual"}</p>
      <div className="mt-auto flex flex-wrap gap-2">
        <Button size="sm" onClick={() => onDownload(entry)}><Download className="mr-2 h-4 w-4" /> Download</Button>
        <Button size="sm" variant="secondary" onClick={() => onView(entry)}><Eye className="mr-2 h-4 w-4" /> View</Button>
        <Button size="sm" variant="secondary" onClick={() => onRegenerate(entry)}><RotateCw className="mr-2 h-4 w-4" /> Regenerate</Button>
        <Button size="sm" variant="secondary" onClick={() => onClone(entry)}><Copy className="mr-2 h-4 w-4" /> Clone</Button>
        <Button size="sm" variant="secondary" onClick={() => onDelete(entry)} className="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/50"><Trash2 className="mr-2 h-4 w-4" /> Delete</Button>
      </div>
    </Card>
  );
}
