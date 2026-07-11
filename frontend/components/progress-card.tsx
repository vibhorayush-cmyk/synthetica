import { LoaderCircle } from "lucide-react";
import { Card } from "@/components/ui/card";

export function ProgressCard() { return <Card className="border-brand-200 bg-brand-50/60 dark:border-brand-500/30 dark:bg-brand-500/10"><div className="flex items-center gap-3"><LoaderCircle className="h-5 w-5 animate-spin text-brand-600" /><div><p className="font-semibold">Generating your dataset</p><p className="mt-1 text-sm text-slate-600 dark:text-slate-400">Building tables, applying scenario and quality rules, then packaging your download.</p></div></div></Card>; }
