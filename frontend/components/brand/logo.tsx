import { cn } from "@/lib/utils";

export function Logo({ className, title }: { className?: string; title?: string }) {
  return <svg viewBox="0 0 48 48" role={title ? "img" : undefined} aria-hidden={title ? undefined : true} className={cn("shrink-0", className)} fill="none" xmlns="http://www.w3.org/2000/svg">{title && <title>{title}</title>}<rect width="48" height="48" rx="14" fill="currentColor" /><path d="M13 15.5h12.5v8H13zM22.5 25h12.5v8H22.5z" stroke="white" strokeWidth="2.5" strokeLinejoin="round" /><path d="M15 34c4 0 4-7 8-7s4 7 8 7 4-7 8-7" stroke="white" strokeWidth="2.5" strokeLinecap="round" /><circle cx="13" cy="15.5" r="2.5" fill="white" /><circle cx="35" cy="25" r="2.5" fill="white" /></svg>;
}
