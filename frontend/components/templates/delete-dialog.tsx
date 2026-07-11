"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export function DeleteDialog({
  open,
  onCancel,
  onConfirm,
  title,
}: {
  open: boolean;
  onCancel: () => void;
  onConfirm: () => void;
  title: string;
}) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/70 p-4">
      <Card className="w-full max-w-md space-y-4">
        <div>
          <h3 className="text-lg font-semibold">Delete template</h3>
          <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{title}</p>
        </div>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
          <Button onClick={onConfirm} className="bg-red-600 hover:bg-red-700">
            Delete
          </Button>
        </div>
      </Card>
    </div>
  );
}
