"use client";

import { useEffect, useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { DatasetSummary } from "@/components/dataset-summary";
import { GenerateDatasetForm } from "@/components/generate-dataset-form";
import { ThemeToggle } from "@/components/theme-toggle";
import { Toast } from "@/components/ui/toast";
import { useIndustries } from "@/hooks/use-industries";
import type { GenerateResponse } from "@/types/generation";

export default function WorkspacePage() {
  const [result, setResult] = useState<GenerateResponse | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const industries = useIndustries();
  const [selectedIndustry, setSelectedIndustry] = useState<string>();
  useEffect(() => { if (!selectedIndustry && industries.data?.length) setSelectedIndustry(industries.data[0].id); }, [industries.data, selectedIndustry]);
  const plugin = industries.data?.find((item) => item.id === selectedIndustry);

  return <main className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]"><AppSidebar activePlugin={plugin} /><section className="min-w-0 px-4 py-6 sm:px-8 lg:px-12"><div className="mx-auto max-w-6xl"><header className="mb-8 flex items-start justify-between gap-4"><div><p className="mb-2 text-sm font-medium text-brand-600">Synthetica Workspace</p><h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Generate analytics-ready datasets</h1><p className="mt-3 max-w-3xl text-slate-600 dark:text-slate-400">Configure a plugin, add business realism, and download a documented learning bundle.</p></div><ThemeToggle /></header><div className="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_minmax(320px,0.85fr)]"><GenerateDatasetForm plugin={plugin} plugins={industries.data ?? []} onIndustryChange={setSelectedIndustry} onGenerated={(response) => { setResult(response); setToast("Dataset generated successfully."); }} /><DatasetSummary result={result} /></div></div></section>{toast && <Toast message={toast} onClose={() => setToast(null)} />}</main>;
}
