import { Logo } from "@/components/brand/logo";
import { Wordmark } from "@/components/brand/wordmark";

export function BrandLockup({ compact = false, inverse = false }: { compact?: boolean; inverse?: boolean }) {
  return <div className={inverse ? "flex items-center gap-3 text-white" : "flex items-center gap-3 text-brand-600"}><Logo className={compact ? "h-8 w-8" : "h-10 w-10"} /><Wordmark showTagline={!compact} className={inverse ? "[&>span:first-child]:text-white [&>span:last-child]:text-slate-300" : undefined} /></div>;
}
