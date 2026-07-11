"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronDown, Sparkles } from "lucide-react";
import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { useGenerateDataset } from "@/hooks/use-generate-dataset";
import { datasetSchema, type DatasetFormValues } from "@/lib/schemas";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { ProgressCard } from "@/components/progress-card";
import type { GenerateResponse } from "@/types/generation";
import type { ConfigurationField, IndustryPlugin } from "@/types/industry";

const qualityFields = [
  ["missing_values", "Missing Values %"],
  ["duplicates", "Duplicates %"],
  ["outliers", "Outliers %"],
  ["invalid_formats", "Invalid Formats %"],
  ["referential_noise", "Referential Noise %"],
] as const;

type Props = {
  plugin: IndustryPlugin | undefined;
  plugins: IndustryPlugin[];
  onIndustryChange: (industry: string) => void;
  onGenerated: (response: GenerateResponse) => void;
};

export function GenerateDatasetForm({ plugin, plugins, onIndustryChange, onGenerated }: Props) {
  const form = useForm<DatasetFormValues>({ resolver: zodResolver(datasetSchema) });
  const generation = useGenerateDataset();
  const disabled = generation.isPending || !plugin?.generation_available;
  const error = generation.error instanceof Error ? generation.error.message : null;

  useEffect(() => {
    if (!plugin) return;
    form.reset({
      industry: plugin.id,
      scenario: plugin.supported_scenarios?.[0] ?? "none",
      configuration: Object.fromEntries(
        (plugin.configuration_fields ?? []).map((field) => [field.key, field.default])
      ),
      export: "zip",
      quality: { missing_values: 0, duplicates: 0, outliers: 0, invalid_formats: 0, referential_noise: 0 },
    });
  }, [form, plugin]);

  const layout = plugin ? resolveLayout(plugin) : [];
  return <div className="space-y-5"><Card><div className="mb-6"><div className="flex items-center gap-2"><Sparkles className="h-5 w-5 text-brand-600" /><h2 className="text-xl font-bold">Dataset Configuration</h2></div><p className="mt-1 text-sm text-slate-500">{plugin?.description ?? "Loading the industry plugin…"}</p></div><form onSubmit={form.handleSubmit((values) => generation.mutate(values, { onSuccess: onGenerated }))}><fieldset disabled={disabled} className="space-y-5"><div className="grid gap-4 sm:grid-cols-2"><Field label="Industry"><select value={plugin?.id ?? ""} onChange={(event) => onIndustryChange(event.target.value)} className="input" disabled={!plugins.length || generation.isPending}>{plugins.map((item) => <option key={item.id} value={item.id}>{item.name}{item.status === "coming_soon" ? " — Coming Soon" : ""}</option>)}</select></Field><Field label="Scenario"><select {...form.register("scenario")} className="input">{(plugin?.supported_scenarios ?? []).map((scenario) => <option key={scenario} value={scenario}>{humanize(scenario)}</option>)}</select></Field></div>{layout.map((section) => <section key={section.title}><h3 className="mb-3 text-sm font-bold">{section.title}</h3><div className="grid gap-4 sm:grid-cols-2">{section.fields.map((field) => <ConfigurationInput key={field.key} field={field} register={form.register} error={form.formState.errors.configuration?.[field.key]?.message} />)}</div></section>)}<Field label="Export Type"><input className="input" value="ZIP bundle" disabled /><p className="mt-1 text-xs text-slate-500">The active plugin packages all generated artifacts into a ZIP download.</p></Field><details className="group rounded-xl border border-slate-200 px-4 py-3 dark:border-slate-800"><summary className="flex cursor-pointer list-none items-center justify-between font-semibold">Data Quality <ChevronDown className="h-4 w-4 transition group-open:rotate-180" /></summary><div className="mt-4 grid gap-4 sm:grid-cols-2">{qualityFields.map(([name, label]) => <Field key={name} label={label} error={form.formState.errors.quality?.[name]?.message}><input className="input" type="number" min="0" max="100" step="1" {...form.register(`quality.${name}`)} /></Field>)}</div></details></fieldset>{plugin && !plugin.generation_available && <p className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-800 dark:bg-amber-950/40 dark:text-amber-200">This plugin is discoverable and configurable, but generation is coming soon.</p>}{error && <p role="alert" className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700 dark:bg-red-950/40 dark:text-red-300">{error}</p>}<Button className="mt-6 w-full" type="submit" disabled={disabled}>{generation.isPending ? "Generating…" : "Generate Dataset"}</Button></form></Card>{generation.isPending && <ProgressCard />}</div>;
}

function resolveLayout(plugin: IndustryPlugin) {
  const configurationFields = plugin.configuration_fields ?? [];
  const fieldsByKey = new Map(configurationFields.map((field) => [field.key, field]));
  const sections = plugin.field_layout?.length ? plugin.field_layout : [{ title: "Dataset Size", fields: configurationFields.map((field) => field.key), columns: 2 }];
  return sections.map((section) => ({ ...section, fields: section.fields.map((key) => fieldsByKey.get(key)).filter((field): field is ConfigurationField => Boolean(field)) }));
}

function ConfigurationInput({ field, register, error }: { field: ConfigurationField; register: ReturnType<typeof useForm<DatasetFormValues>>["register"]; error?: string }) { return <Field label={field.label} error={error}><input className="input" type={field.type} min={field.minimum} max={field.maximum} {...register(`configuration.${field.key}`)} />{field.help_text && <p className="mt-1 text-xs text-slate-500">{field.help_text}</p>}</Field>; }
function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) { return <label className="block text-sm font-medium text-slate-700 dark:text-slate-300"><span>{label}</span><div className="mt-1.5">{children}</div>{error && <span className="mt-1 block text-xs text-red-600">{error}</span>}</label>; }
function humanize(value: string) { return value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase()); }
