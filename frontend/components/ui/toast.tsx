"use client";

import { CheckCircle2, X } from "lucide-react";
import { Button } from "@/components/ui/button";

export function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  return <div className="fixed bottom-5 right-5 flex items-center gap-3 rounded-xl bg-slate-900 px-4 py-3 text-sm font-medium text-white shadow-xl"><CheckCircle2 className="h-5 w-5 text-emerald-400" />{message}<Button variant="ghost" size="sm" className="h-7 px-1 text-white hover:bg-slate-700" onClick={onClose}><X className="h-4 w-4" /></Button></div>;
}
