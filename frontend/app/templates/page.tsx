"use client";

import { useMemo, useState } from "react";
import { Plus, RotateCcw, Search } from "lucide-react";
import { AppSidebar } from "@/components/app-sidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { TemplateCard } from "@/components/templates/template-card";
import { TemplateFilters } from "@/components/templates/template-filters";
import { TemplateForm } from "@/components/templates/template-form";
import { TemplateSummary } from "@/components/templates/template-summary";
import { DeleteDialog } from "@/components/templates/delete-dialog";
import {
  useCreateTemplate,
  useDeleteTemplate,
  useGenerateFromTemplate,
  useTemplates,
  useUpdateTemplate,
} from "@/hooks/use-templates";
import { useMutation } from "@tanstack/react-query";
import { generateDataset } from "@/services/generation-service";
import type { GenerateResponse } from "@/types/generation";
import type { TemplateFormValues, TemplateRecord } from "@/types/templates";
import { ProtectedPage } from "@/components/protected-page";

export default function TemplatesPage() {
  const [query, setQuery] = useState("");
  const [industry, setIndustry] = useState("all");
  const [difficulty, setDifficulty] = useState("all");
  const [scenario, setScenario] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<TemplateRecord | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<TemplateRecord | null>(null);
  const [summary, setSummary] = useState<GenerateResponse | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  const { data: templates = [], isLoading, error, refetch } = useTemplates();
  const createTemplate = useCreateTemplate();
  const updateTemplate = useUpdateTemplate();
  const deleteTemplate = useDeleteTemplate();
  const generateFromTemplate = useGenerateFromTemplate();
  const directGenerate = useMutation({ mutationFn: generateDataset });

  const filteredTemplates = useMemo(() => {
    const next = templates.filter((template) => {
      const matchesQuery = `${template.name} ${template.description}`.toLowerCase().includes(query.toLowerCase());
      const matchesIndustry = industry === "all" || template.industry === industry;
      const matchesDifficulty = difficulty === "all" || template.difficulty === difficulty;
      const matchesScenario = scenario === "all" || template.scenario === scenario;
      return matchesQuery && matchesIndustry && matchesDifficulty && matchesScenario;
    });

    next.sort((left, right) => {
      if (sortBy === "oldest") {
        return new Date(left.created_at).getTime() - new Date(right.created_at).getTime();
      }
      if (sortBy === "alphabetical") {
        return left.name.localeCompare(right.name);
      }
      return new Date(right.created_at).getTime() - new Date(left.created_at).getTime();
    });

    return next;
  }, [difficulty, industry, query, scenario, sortBy, templates]);

  function openCreate() {
    setSelectedTemplate(null);
    setIsFormOpen(true);
  }

  function handleSubmit(payload: TemplateFormValues) {
    if (selectedTemplate) {
      updateTemplate.mutate(
        { id: selectedTemplate.id, payload },
        {
          onSuccess: () => {
            setIsFormOpen(false);
            setSelectedTemplate(null);
            setToast("Template updated.");
          },
          onError: (error) => setToast(error.message),
        },
      );
      return;
    }

    createTemplate.mutate(payload, {
      onSuccess: () => {
        setIsFormOpen(false);
        setToast("Template created.");
      },
      onError: (error) => setToast(error.message),
    });
  }

  function handleDuplicate(template: TemplateRecord) {
    const payload = {
      ...template,
      id: "",
      name: `${template.name} Copy`,
      description: template.description,
      created_at: "",
      updated_at: "",
      version: 1,
    } as TemplateRecord;
    setSelectedTemplate(null);
    setIsFormOpen(true);
    // Keep the form prefilled by letting the modal use the selected template to populate values.
    setSelectedTemplate(payload);
  }

  function handleGenerate(template: TemplateRecord) {
    generateFromTemplate.mutate(template.id, {
      onSuccess: (response) => {
        setSummary(response);
        setToast("Dataset generated successfully.");
      },
      onError: (error) => setToast(error.message),
    });
  }

  function handleDelete(template: TemplateRecord) {
    setDeleteTarget(template);
  }

  function confirmDelete() {
    if (!deleteTarget) return;
    deleteTemplate.mutate(deleteTarget.id, {
      onSuccess: () => {
        setDeleteTarget(null);
        setToast("Template deleted.");
      },
      onError: (error) => setToast(error.message),
    });
  }

  return (
    <ProtectedPage><main className="min-h-screen lg:grid lg:grid-cols-[250px_1fr]">
      <AppSidebar />
      <section className="min-w-0 px-4 py-6 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-6xl space-y-6">
          <header className="flex items-start justify-between gap-4">
            <div>
              <p className="mb-2 text-sm font-medium text-brand-600">Templates</p>
              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Templates</h1>
              <p className="mt-3 max-w-3xl text-slate-600 dark:text-slate-400">Save, reuse and share dataset configurations.</p>
            </div>
            <ThemeToggle />
          </header>

          <Card className="p-0">
            <div className="flex flex-col gap-4 border-b border-slate-200 p-5 dark:border-slate-800 md:flex-row md:items-center md:justify-between">
              <div>
                <h2 className="text-xl font-semibold">Template Library</h2>
                <p className="mt-1 text-sm text-slate-500">Browse, edit, and generate datasets from saved configurations.</p>
              </div>
              <Button onClick={openCreate}>
                <Plus className="mr-2 h-4 w-4" /> Create Template
              </Button>
            </div>
            <div className="space-y-5 p-5">
              <TemplateFilters query={query} setQuery={setQuery} industry={industry} setIndustry={setIndustry} difficulty={difficulty} setDifficulty={setDifficulty} scenario={scenario} setScenario={setScenario} sortBy={sortBy} setSortBy={setSortBy} />
              {summary ? <TemplateSummary result={summary} onReset={() => setSummary(null)} /> : null}
              {isLoading ? (
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {Array.from({ length: 3 }).map((_, index) => <div key={index} className="h-56 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />)}
                </div>
              ) : null}
              {error ? (
                <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm text-red-700 dark:border-red-800 dark:bg-red-950/30 dark:text-red-300">
                  <p className="font-semibold">We could not load your templates.</p>
                  <Button variant="secondary" className="mt-3" onClick={() => refetch()}>
                    <RotateCcw className="mr-2 h-4 w-4" /> Retry
                  </Button>
                </div>
              ) : null}
              {!isLoading && !error && filteredTemplates.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500 dark:border-slate-700">
                  <p className="font-semibold text-slate-800 dark:text-slate-200">No templates found</p>
                  <p className="mt-2">Create your first template to save a reusable dataset configuration.</p>
                  <Button className="mt-4" onClick={openCreate}>
                    <Plus className="mr-2 h-4 w-4" /> Create Template
                  </Button>
                </div>
              ) : null}
              {!isLoading && !error && filteredTemplates.length > 0 ? (
                <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                  {filteredTemplates.map((template) => (
                    <TemplateCard key={template.id} template={template} onGenerate={handleGenerate} onEdit={(item) => { setSelectedTemplate(item); setIsFormOpen(true); }} onDuplicate={handleDuplicate} onDelete={handleDelete} />
                  ))}
                </div>
              ) : null}
            </div>
          </Card>
        </div>
      </section>

      {isFormOpen ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/70 p-4">
          <Card className="w-full max-w-4xl max-h-[90vh] overflow-y-auto p-5">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h3 className="text-xl font-semibold">{selectedTemplate ? "Edit Template" : "Create Template"}</h3>
                <p className="mt-1 text-sm text-slate-500">Save reusable dataset settings for future runs.</p>
              </div>
              <Button variant="secondary" onClick={() => { setIsFormOpen(false); setSelectedTemplate(null); }}>
                Close
              </Button>
            </div>
            <TemplateForm initialValues={selectedTemplate ?? undefined} onSubmit={handleSubmit} submitting={createTemplate.isPending || updateTemplate.isPending} submitLabel={selectedTemplate ? "Save Template" : "Create Template"} />
          </Card>
        </div>
      ) : null}

      <DeleteDialog open={Boolean(deleteTarget)} onCancel={() => setDeleteTarget(null)} onConfirm={confirmDelete} title={deleteTarget ? `Delete “${deleteTarget.name}”?` : "Delete this template?"} />
      {toast ? <div className="fixed bottom-5 right-5 rounded-xl bg-slate-900 px-4 py-3 text-sm font-medium text-white shadow-xl">{toast}</div> : null}
    </main></ProtectedPage>
  );
}
