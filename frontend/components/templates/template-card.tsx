"use client";

import { Copy, Pencil, Sparkles, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { TemplateRecord } from "@/types/templates";

export function TemplateCard({
  template,
  onGenerate,
  onEdit,
  onDuplicate,
  onDelete,
}: {
  template: TemplateRecord;
  onGenerate: (template: TemplateRecord) => void;
  onEdit: (template: TemplateRecord) => void;
  onDuplicate: (template: TemplateRecord) => void;
  onDelete: (template: TemplateRecord) => void;
}) {
  return (
    <Card className="flex h-full flex-col gap-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-brand-600" />
            <h3 className="text-lg font-semibold">{template.name}</h3>
          </div>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{template.description}</p>
        </div>
        <span className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700 dark:bg-brand-500/15 dark:text-brand-400">
          {template.difficulty}
        </span>
      </div>

      <div className="flex flex-wrap gap-2 text-xs text-slate-500">
        <span className="rounded-full bg-slate-100 px-2.5 py-1 dark:bg-slate-800">{template.industry}</span>
        <span className="rounded-full bg-slate-100 px-2.5 py-1 dark:bg-slate-800">{template.scenario.replace(/_/g, " ")}</span>
      </div>

      <dl className="grid gap-3 text-sm text-slate-600 dark:text-slate-400 sm:grid-cols-2">
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-400">Table counts</dt>
          <dd>{template.customers.toLocaleString()} customers / {template.orders.toLocaleString()} orders</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-400">Quality</dt>
          <dd>{Object.values(template.quality).filter((value) => value > 0).length} issues configured</dd>
        </div>
      </dl>

      <p className="text-sm text-slate-500">Created {new Date(template.created_at).toLocaleDateString()}</p>

      <div className="mt-auto flex flex-wrap gap-2">
        <Button size="sm" onClick={() => onGenerate(template)}>
          Generate
        </Button>
        <Button size="sm" variant="secondary" onClick={() => onEdit(template)}>
          <Pencil className="mr-2 h-4 w-4" /> Edit
        </Button>
        <Button size="sm" variant="secondary" onClick={() => onDuplicate(template)}>
          <Copy className="mr-2 h-4 w-4" /> Duplicate
        </Button>
        <Button size="sm" variant="secondary" onClick={() => onDelete(template)} className="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/50">
          <Trash2 className="mr-2 h-4 w-4" /> Delete
        </Button>
      </div>
    </Card>
  );
}
