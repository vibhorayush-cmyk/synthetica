import type { HTMLAttributes } from "react";
import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return <section className={cn("surface rounded-2xl p-5 shadow-card sm:p-6", className)} {...props} />;
}
