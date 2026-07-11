"use client";

import { Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { GenerateResponse } from "@/types/generation";

export function TemplateSummary({
  result,
  onReset,
}: {
  result: GenerateResponse | null;
  onReset: () => void;
}) {
  if (!result) {
    return null;
  }

  return (
    <div className="space-y-4 rounded-2xl border border-emerald-200 bg-emerald-50 p-5 dark:border-emerald-800 dark:bg-emerald-950/30">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-emerald-800 dark:text-emerald-300">Dataset generated</p>
          <p className="mt-1 text-sm text-emerald-700 dark:text-emerald-400">{result.challenge_title}</p>
        </div>
        <Button variant="secondary" onClick={onReset}>
          Clear
        </Button>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <div className="rounded-xl bg-white/80 p-3 dark:bg-slate-900/60">
          <p className="text-xs uppercase tracking-wide text-slate-400">Difficulty</p>
          <p className="mt-1 font-semibold">{result.difficulty}</p>
        </div>
        <div className="rounded-xl bg-white/80 p-3 dark:bg-slate-900/60">
          <p className="text-xs uppercase tracking-wide text-slate-400">Estimated time</p>
          <p className="mt-1 font-semibold">{result.estimated_time}</p>
        </div>
        <div className="rounded-xl bg-white/80 p-3 dark:bg-slate-900/60">
          <p className="text-xs uppercase tracking-wide text-slate-400">Scenario</p>
          <p className="mt-1 font-semibold">{result.scenario}</p>
        </div>
      </div>
      {result.download_url ? (
        <a href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/downloads/${result.download_url}`} target="_blank" rel="noreferrer">
          <Button className="w-full md:w-auto">
            <Download className="mr-2 h-4 w-4" /> Download ZIP
          </Button>
        </a>
      ) : null}
    </div>
  );
}
