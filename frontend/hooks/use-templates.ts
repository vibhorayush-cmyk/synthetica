"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  createTemplate,
  deleteTemplate,
  fetchTemplate,
  fetchTemplates,
  generateFromTemplate,
  updateTemplate,
} from "@/services/templates-service";
import type { TemplateFormValues } from "@/types/templates";

export function useTemplates() {
  return useQuery({ queryKey: ["templates"], queryFn: fetchTemplates });
}

export function useTemplate(id: string) {
  return useQuery({ queryKey: ["templates", id], queryFn: () => fetchTemplate(id), enabled: Boolean(id) });
}

export function useCreateTemplate() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (payload: TemplateFormValues) => createTemplate(payload),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["templates"] });
    },
  });
}

export function useUpdateTemplate() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: TemplateFormValues }) => updateTemplate(id, payload),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["templates"] });
    },
  });
}

export function useDeleteTemplate() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteTemplate(id),
    onSuccess: () => {
      client.invalidateQueries({ queryKey: ["templates"] });
    },
  });
}

export function useGenerateFromTemplate() {
  return useMutation({ mutationFn: (id: string) => generateFromTemplate(id) });
}
