"use client";

import { useMemo, useState } from "react";
import { Plus, RotateCcw } from "lucide-react";
import Link from "next/link";
import { AppSidebar } from "@/components/app-sidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { HistoryCard } from "@/components/history/history-card";
import { HistoryFilters } from "@/components/history/history-filters";
import { HistoryDetails } from "@/components/history/history-details";
import { useCloneHistoryEntry, useDeleteHistoryEntry, useHistory, useRegenerateHistoryEntry } from "@/hooks/use-history";
import type { HistoryEntry } from "@/types/history";
import { ProtectedPage } from "@/components/protected-page";
import { authenticatedDownload } from "@/services/api-client";

export default function HistoryPage() {
  const [query, setQuery] = useState("");
  const [industry, setIndustry] = useState("all");
  const [scenario, setScenario] = useState("all");
  const [dateFilter, setDateFilter] = useState("all");
  const [status, setStatus] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [selectedEntry, setSelectedEntry] = useState<HistoryEntry | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const { data: history = [], isLoading, error, refetch } = useHistory();
  const deleteMutation = useDeleteHistoryEntry();
  const regenerateMutation = useRegenerateHistoryEntry();
  const cloneMutation = useCloneHistoryEntry();

  const filteredHistory = useMemo(() => {
    const next = history.filter((entry) => {
      const matchesQuery = `${entry.dataset_name} ${entry.industry} ${entry.scenario}`.toLowerCase().includes(query.toLowerCase());
      const matchesIndustry = industry === "all" || entry.industry === industry;
      const matchesScenario = scenario === "all" || entry.scenario === scenario;
      const matchesStatus = status === "all" || entry.status === status;
      const generatedDate = new Date(entry.generated_at);
      const today = new Date();
      const matchesDate = dateFilter === "all" || (dateFilter === "today" && generatedDate.toDateString() === today.toDateString()) || (dateFilter === "week" && generatedDate.getTime() > today.getTime() - 7 * 24 * 60 * 60 * 1000);
      return matchesQuery && matchesIndustry && matchesScenario && matchesStatus && matchesDate;
    });

    next.sort((left, right) => {
      if (sortBy === "oldest") return new Date(left.generated_at).getTime() - new Date(right.generated_at).getTime();
      if (sortBy === "largest") return right.zip_size - left.zip_size;
      return new Date(right.generated_at).getTime() - new Date(left.generated_at).getTime();
    });

    return next;
  }, [dateFilter, history, industry, query, scenario, sortBy, status]);

  const stats = useMemo(() => {
    const total = history.length;
    const today = history.filter((entry) => new Date(entry.generated_at).toDateString() === new Date().toDateString()).length;
    const averageDuration = history.length > 0 ? Math.round(history.reduce((sum, entry) => sum + entry.generation_duration_ms, 0) / history.length) : 0;
    const mostUsedScenario = history.reduce<Record<string, number>>((acc, entry) => {
      acc[entry.scenario] = (acc[entry.scenario] ?? 0) + 1;
      return acc;
    }, {});
    const scenario = Object.entries(mostUsedScenario).sort((left, right) => right[1] - left[1])[0]?.[0] ?? "None";
    const industry = history.reduce<Record<string, number>>((acc, entry) => {
      acc[entry.industry] = (acc[entry.industry] ?? 0) + 1;
      return acc;
    }, {});
    const mostUsedIndustry = Object.entries(industry).sort((left, right) => right[1] - left[1])[0]?.[0] ?? "Retail";
    return { total, today, averageDuration, scenario, mostUsedIndustry, totalDownloadSize: history.reduce((sum, entry) => sum + entry.zip_size, 0) };
  }, [history]);

  function handleDownload(entry: HistoryEntry) {
    void authenticatedDownload(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/downloads/${entry.zip_filename}`);
  }

  function handleRegenerate(entry: HistoryEntry) {
    regenerateMutation.mutate(entry.id, {
      onSuccess: () => setToast("Dataset regeneration started."),
      onError: (error) => setToast(error.message),
    });
  }

  function handleClone(entry: HistoryEntry) {
    cloneMutation.mutate(entry.id, {
      onSuccess: () => setToast("Dataset cloned."),
      onError: (error) => setToast(error.message),
    });
  }

  function handleDelete(entry: HistoryEntry) {
    deleteMutation.mutate(entry.id, {
      onSuccess: () => setToast("Dataset deleted."),
      onError: (error) => setToast(error.message),
    });
  }

  return (
    <ProtectedPage><main className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]">
      <AppSidebar />
      <section className="min-w-0 px-4 py-6 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-7xl space-y-6">
          <header className="flex items-start justify-between gap-4">
            <div>
              <p className="mb-2 text-sm font-medium text-brand-600">History</p>
              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Generation History</h1>
              <p className="mt-3 max-w-3xl text-slate-600 dark:text-slate-400">Manage previously generated datasets.</p>
            </div>
            <ThemeToggle />
          </header>

          <div className="grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
            <Card className="p-0">
              <div className="flex flex-col gap-4 border-b border-slate-200 p-5 dark:border-slate-800 md:flex-row md:items-center md:justify-between">
                <div>
                  <h2 className="text-xl font-semibold">Workspace</h2>
                  <p className="mt-1 text-sm text-slate-500">Search, re-download, clone and regenerate your datasets.</p>
                </div>
                <Link href="/workspace">
                  <Button>
                    <Plus className="mr-2 h-4 w-4" /> Generate First Dataset
                  </Button>
                </Link>
              </div>
              <div className="space-y-5 p-5">
                <HistoryFilters query={query} setQuery={setQuery} industry={industry} setIndustry={setIndustry} scenario={scenario} setScenario={setScenario} dateFilter={dateFilter} setDateFilter={setDateFilter} status={status} setStatus={setStatus} sortBy={sortBy} setSortBy={setSortBy} />
                {isLoading ? <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-2">{Array.from({ length: 4 }).map((_, index) => <div key={index} className="h-56 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />)}</div> : null}
                {error ? <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/30 dark:text-red-300"><p className="font-semibold">We could not load your generation history.</p><Button variant="secondary" className="mt-3" onClick={() => refetch()}><RotateCcw className="mr-2 h-4 w-4" /> Retry</Button></div> : null}
                {!isLoading && !error && filteredHistory.length === 0 ? <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500 dark:border-slate-700"><p className="font-semibold text-slate-800 dark:text-slate-200">No datasets generated yet.</p><p className="mt-2">Start by generating your first dataset and it will appear here.</p><Link href="/workspace" className="mt-4 inline-flex"><Button>Generate First Dataset</Button></Link></div> : null}
                {!isLoading && !error && filteredHistory.length > 0 ? <div className="grid gap-4 xl:grid-cols-2">{filteredHistory.map((entry) => <HistoryCard key={entry.id} entry={entry} onView={setSelectedEntry} onDownload={handleDownload} onRegenerate={handleRegenerate} onClone={handleClone} onDelete={handleDelete} />)}</div> : null}
              </div>
            </Card>
            <div className="space-y-4">
              <Card>
                <h3 className="text-lg font-semibold">Statistics</h3>
                <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                  <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900"><p className="text-xs uppercase tracking-wide text-slate-400">Total datasets</p><p className="mt-1 text-2xl font-semibold">{stats.total}</p></div>
                  <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900"><p className="text-xs uppercase tracking-wide text-slate-400">Generated today</p><p className="mt-1 text-2xl font-semibold">{stats.today}</p></div>
                  <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900"><p className="text-xs uppercase tracking-wide text-slate-400">Average generation time</p><p className="mt-1 text-2xl font-semibold">{stats.averageDuration} ms</p></div>
                  <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900"><p className="text-xs uppercase tracking-wide text-slate-400">Most used scenario</p><p className="mt-1 text-2xl font-semibold">{stats.scenario}</p></div>
                  <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900"><p className="text-xs uppercase tracking-wide text-slate-400">Most used industry</p><p className="mt-1 text-2xl font-semibold">{stats.mostUsedIndustry}</p></div>
                  <div className="rounded-xl bg-slate-50 p-4 dark:bg-slate-900"><p className="text-xs uppercase tracking-wide text-slate-400">Total download size</p><p className="mt-1 text-2xl font-semibold">{stats.totalDownloadSize} bytes</p></div>
                </div>
              </Card>
              <HistoryDetails entry={selectedEntry} />
            </div>
          </div>
        </div>
      </section>
      {toast ? <div className="fixed bottom-5 right-5 rounded-xl bg-slate-900 px-4 py-3 text-sm font-medium text-white shadow-xl">{toast}</div> : null}
    </main></ProtectedPage>
  );
}
