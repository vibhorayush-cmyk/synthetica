"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { templateSchema, type TemplateFormSchema } from "@/lib/templates-schemas";
import type { TemplateFormValues, TemplateRecord } from "@/types/templates";

const qualityFields = [
  ["missing_values", "Missing Values %"],
  ["duplicates", "Duplicates %"],
  ["outliers", "Outliers %"],
  ["invalid_formats", "Invalid Formats %"],
  ["referential_noise", "Referential Noise %"],
] as const;

const defaultValues: TemplateFormValues = {
  name: "",
  description: "",
  industry: "retail",
  scenario: "none",
  customers: 1000,
  products: 100,
  stores: 10,
  orders: 5000,
  export_type: "zip",
  quality: {
    missing_values: 0,
    duplicates: 0,
    outliers: 0,
    invalid_formats: 0,
    referential_noise: 0,
  },
  difficulty: "Beginner",
};

export function TemplateForm({
  initialValues,
  onSubmit,
  submitting,
  submitLabel,
}: {
  initialValues?: TemplateRecord;
  onSubmit: (payload: TemplateFormValues) => void;
  submitting?: boolean;
  submitLabel: string;
}) {
  const form = useForm<TemplateFormSchema>({
    resolver: zodResolver(templateSchema),
    defaultValues: initialValues ? mapTemplateToForm(initialValues) : defaultValues,
  });

  useEffect(() => {
    if (initialValues) {
      form.reset(mapTemplateToForm(initialValues));
    }
  }, [form, initialValues]);

  return (
    <form onSubmit={form.handleSubmit((values) => onSubmit(values as TemplateFormValues))} className="space-y-5">
      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Name" error={form.formState.errors.name?.message}>
          <input className="input" {...form.register("name")} />
        </Field>
        <Field label="Difficulty" error={form.formState.errors.difficulty?.message}>
          <select className="input" {...form.register("difficulty")}>
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>
        </Field>
      </div>

      <Field label="Description" error={form.formState.errors.description?.message}>
        <textarea className="input min-h-[96px]" {...form.register("description")} />
      </Field>

      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Industry" error={form.formState.errors.industry?.message}>
          <select className="input" {...form.register("industry")}>
            <option value="retail">Retail</option>
          </select>
        </Field>
        <Field label="Scenario" error={form.formState.errors.scenario?.message}>
          <select className="input" {...form.register("scenario")}>
            <option value="none">None</option>
            <option value="black_friday">Black Friday</option>
            <option value="christmas">Christmas</option>
            <option value="summer_sale">Summer Sale</option>
            <option value="recession">Recession</option>
          </select>
        </Field>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {(["customers", "products", "stores", "orders"] as const).map((field) => (
          <Field key={field} label={field[0].toUpperCase() + field.slice(1)} error={form.formState.errors[field]?.message}>
            <input className="input" type="number" min="1" {...form.register(field)} />
          </Field>
        ))}
      </div>

      <Field label="Export Type" error={form.formState.errors.export_type?.message}>
        <input className="input" placeholder="zip" {...form.register("export_type")} />
      </Field>

      <div className="space-y-3 rounded-2xl border border-slate-200 p-4 dark:border-slate-800">
        <p className="text-sm font-semibold">Quality Settings</p>
        <div className="grid gap-3 md:grid-cols-2">
          {qualityFields.map(([name, label]) => (
            <Field key={name} label={label} error={form.formState.errors.quality?.[name]?.message}>
              <input
                className="input"
                type="number"
                min="0"
                max="100"
                {...form.register(`quality.${name}`)}
              />
            </Field>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-3">
        <Button type="button" variant="secondary" onClick={() => form.reset(defaultValues)}>
          Reset
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : submitLabel}
        </Button>
      </div>
    </form>
  );
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return (
    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
      <span>{label}</span>
      <div className="mt-1.5">{children}</div>
      {error ? <span className="mt-1 block text-xs text-red-600">{error}</span> : null}
    </label>
  );
}

function mapTemplateToForm(template: TemplateRecord): TemplateFormValues {
  return {
    name: template.name,
    description: template.description,
    industry: template.industry,
    scenario: template.scenario,
    customers: template.customers,
    products: template.products,
    stores: template.stores,
    orders: template.orders,
    export_type: template.export_type,
    quality: template.quality,
    difficulty: template.difficulty,
  };
}
