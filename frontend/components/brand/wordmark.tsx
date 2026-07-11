import { brand } from "@/lib/brand";
import { cn } from "@/lib/utils";

export function Wordmark({ className, showTagline = false }: { className?: string; showTagline?: boolean }) {
  return <span className={cn("flex flex-col", className)}><span className="text-lg font-bold tracking-tight text-slate-950 dark:text-white">{brand.name}</span>{showTagline && <span className="text-xs text-slate-500 dark:text-slate-400">{brand.tagline}</span>}</span>;
}
