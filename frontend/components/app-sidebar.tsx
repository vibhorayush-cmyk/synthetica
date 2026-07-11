"use client";

import { BookOpen, Clock3, Database, LayoutDashboard, Library, Settings, Workflow } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { BrandLockup } from "@/components/brand/brand-lockup";
import type { IndustryPlugin } from "@/types/industry";

const navigation = [
  { label: "Dashboard", href: "/workspace", icon: LayoutDashboard },
  { label: "Generate Dataset", href: "/workspace", icon: Database },
  { label: "Templates", href: "/templates", icon: Library },
  { label: "History", href: "/history", icon: Clock3 },
  { label: "Documentation", href: "/docs", icon: BookOpen },
  { label: "Settings", href: "/settings", icon: Settings },
  { label: "Schema Designer", href: "/schema-designer", icon: Workflow },
];

export function AppSidebar({ activePlugin }: { activePlugin?: IndustryPlugin }) {
  const pathname = usePathname();
  return <aside className="surface border-x-0 border-t-0 px-4 py-5 lg:min-h-screen lg:border-r lg:px-5 lg:py-7"><Link href="/" aria-label="Synthetica home" className="mb-7 block"><BrandLockup compact /></Link><nav className="flex gap-2 overflow-x-auto lg:block lg:space-y-1">{navigation.map(({ label, href, icon: Icon }) => <Link key={label} href={href} className={cn("flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition lg:w-full", pathname === href ? "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-500" : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800")}><Icon className="h-4 w-4" />{label}</Link>)}</nav><div className="mt-8 hidden rounded-xl bg-slate-100 p-4 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-400 lg:block"><p className="font-semibold text-slate-800 dark:text-slate-200">{activePlugin?.name ?? "Active plugin"}</p><p className="mt-1.5 leading-5">{activePlugin?.description ?? "Choose an industry plugin to configure its generation workspace."}</p></div></aside>;
}
