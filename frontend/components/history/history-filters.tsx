"use client";

export function HistoryFilters({
  query,
  setQuery,
  industry,
  setIndustry,
  scenario,
  setScenario,
  dateFilter,
  setDateFilter,
  status,
  setStatus,
  sortBy,
  setSortBy,
}: {
  query: string;
  setQuery: (value: string) => void;
  industry: string;
  setIndustry: (value: string) => void;
  scenario: string;
  setScenario: (value: string) => void;
  dateFilter: string;
  setDateFilter: (value: string) => void;
  status: string;
  setStatus: (value: string) => void;
  sortBy: string;
  setSortBy: (value: string) => void;
}) {
  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-6">
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Search</span>
        <input className="input" placeholder="Search history" value={query} onChange={(event) => setQuery(event.target.value)} />
      </label>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Industry</span>
        <select className="input" value={industry} onChange={(event) => setIndustry(event.target.value)}>
          <option value="all">All</option>
          <option value="retail">Retail</option>
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
        <span className="mb-1 block">Date</span>
        <select className="input" value={dateFilter} onChange={(event) => setDateFilter(event.target.value)}>
          <option value="all">All</option>
          <option value="today">Today</option>
          <option value="week">Last 7 days</option>
        </select>
      </label>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Status</span>
        <select className="input" value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="all">All</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="in_progress">In progress</option>
        </select>
      </label>
      <label className="text-sm font-medium text-slate-700 dark:text-slate-300">
        <span className="mb-1 block">Sort</span>
        <select className="input" value={sortBy} onChange={(event) => setSortBy(event.target.value)}>
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="largest">Largest Dataset</option>
        </select>
      </label>
    </div>
  );
}
