import type { TemplateFormValues, TemplateRecord } from "@/types/templates";
import { apiRequest } from "@/services/api-client";

export async function fetchTemplates(): Promise<TemplateRecord[]> {
  return apiRequest<TemplateRecord[]>("/templates");
}

export async function fetchTemplate(id: string): Promise<TemplateRecord> {
  return apiRequest<TemplateRecord>(`/templates/${id}`);
}

export async function createTemplate(payload: TemplateFormValues): Promise<TemplateRecord> {
  return apiRequest<TemplateRecord>("/templates", { method: "POST", body: JSON.stringify(payload) });
}

export async function updateTemplate(id: string, payload: TemplateFormValues): Promise<TemplateRecord> {
  return apiRequest<TemplateRecord>(`/templates/${id}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function deleteTemplate(id: string): Promise<void> {
  await apiRequest<void>(`/templates/${id}`, { method: "DELETE" });
}

export async function generateFromTemplate(id: string): Promise<import("@/types/generation").GenerateResponse> {
  return apiRequest<import("@/types/generation").GenerateResponse>(`/templates/generate/from-template/${id}`, { method: "POST" });
}
