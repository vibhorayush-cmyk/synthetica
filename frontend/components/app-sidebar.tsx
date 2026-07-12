"use client";

import { BookOpen, Clock3, Database, LayoutDashboard, Library, LogIn, LogOut, Settings, UserRound, Workflow } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { cn } from "@/lib/utils";
import { BrandLockup } from "@/components/brand/brand-lockup";
import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";
import type { IndustryPlugin } from "@/types/industry";

const guestNavigation = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Documentation", href: "/docs", icon: BookOpen },
  { label: "Login", href: "/login", icon: LogIn },
  { label: "Register", href: "/register", icon: UserRound },
];
const userNavigation = [
  { label: "Workspace", href: "/workspace", icon: Database },
  { label: "Templates", href: "/templates", icon: Library },
  { label: "History", href: "/history", icon: Clock3 },
  { label: "Profile", href: "/profile", icon: UserRound },
  { label: "Account Settings", href: "/settings", icon: Settings },
  { label: "Schema Designer", href: "/schema-designer", icon: Workflow },
];

export function AppSidebar({ activePlugin }: { activePlugin?: IndustryPlugin }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const navigation = user ? userNavigation : guestNavigation;
  return <aside className="surface border-x-0 border-t-0 px-4 py-5 lg:min-h-screen lg:border-r lg:px-5 lg:py-7">
    <Link href="/" aria-label="Synthetica home" className="mb-7 block"><BrandLockup compact /></Link>
    <nav className="flex gap-2 overflow-x-auto lg:block lg:space-y-1">
      {navigation.map(({ label, href, icon: Icon }) => <Link key={label} href={href} className={cn("flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition lg:w-full", pathname === href ? "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-500" : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800")}><Icon className="h-4 w-4" />{label}</Link>)}
    </nav>
    {!loading && user ? <div className="mt-7 rounded-xl bg-slate-100 p-3 dark:bg-slate-800"><Link href="/profile" className="flex items-center gap-3"><div className="grid h-9 w-9 place-items-center rounded-full bg-brand-600 text-sm font-bold text-white">{user.full_name.slice(0, 1).toUpperCase()}</div><div className="min-w-0"><p className="truncate text-sm font-semibold">{user.full_name}</p><p className="truncate text-xs text-slate-500">{user.email}</p></div></Link><Button variant="secondary" className="mt-3 w-full" onClick={() => void logout().then(() => router.push("/"))}><LogOut className="mr-2 h-4 w-4" />Logout</Button></div> : null}
    {user ? <div className="mt-5 hidden rounded-xl bg-slate-100 p-4 text-xs text-slate-600 dark:bg-slate-800 dark:text-slate-400 lg:block"><p className="font-semibold text-slate-800 dark:text-slate-200">{activePlugin?.name ?? "Your workspace"}</p><p className="mt-1.5 leading-5">{activePlugin?.description ?? "Generate and manage datasets owned by your account."}</p></div> : null}
  </aside>;
}
