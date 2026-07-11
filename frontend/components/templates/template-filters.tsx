"use client";

import type { TemplateRecord } from "@/types/templates";

export function TemplateFilters({
  query,
  setQuery,
  industry,
  setIndustry,
  difficulty,
  setDifficulty,
  scenario,
  setScenario,
  sortBy,
  setSortBy,
}: {
  query: string;
  setQuery: (value: string) => void;
  industry: string;
  setIndustry: (value: string) => void;
  difficulty: string;
  setDifficulty: (value: string) => void;
  scenario: string;
  setScenario: (value: string) => void;
  sortBy: string;
  setSortBy: (value: string) => void;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Search</span>
        <input className="input" placeholder="Search templates" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Industry</span>
        <select className="input" value={industry} onChange={(event) => setIndustry(event.target.value)}>
          <option value="all">All</option>
          <option value="retail">Retail</option>
        </select>
      </label>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Difficulty</span>
        <select className="input" value={difficulty} onChange={(event) => setDifficulty(event.target.value)}>
          <option value="all">All</option>
          <option value="Beginner">Beginner</option>
          <option value="Intermediate">Intermediate</option>
          <option value="Advanced">Advanced</option>
        </select>
      </label>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Scenario</span>
        <select className="input" value={scenario} onChange={(event) => setScenario(event.target.value)}>
          <option value="all">All</option>
          <option value="none">None</option>
          <option value="black_friday">Black Friday</option>
          <option value="christmas">Christmas</option>
          <option value="summer_sale">Summer Sale</option>
          <option value="recession">Recession</option>
        </select>
      </label>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Sort</span>
        <select className="input" value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="alphabetical">Alphabetical</option>
        </select>
      </label>
    </div>
  );
}
