import type { TemplateFormValues, TemplateRecord } from "@/types/templates";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiUrl}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed.");
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function fetchTemplates(): Promise<TemplateRecord[]> {
  return request<TemplateRecord[]>("/templates");
}

export async function fetchTemplate(id: string): Promise<TemplateRecord> {
  return request<TemplateRecord>(`/templates/${id}`);
}

export async function createTemplate(payload: TemplateFormValues): Promise<TemplateRecord> {
  return request<TemplateRecord>("/templates", { method: "POST", body: JSON.stringify(payload) });
}

export async function updateTemplate(id: string, payload: TemplateFormValues): Promise<TemplateRecord> {
  return request<TemplateRecord>(`/templates/${id}`, { method: "PUT", body: JSON.stringify(payload) });
}

export async function deleteTemplate(id: string): Promise<void> {
  await request<void>(`/templates/${id}`, { method: "DELETE" });
}

export async function generateFromTemplate(id: string): Promise<import("@/types/generation").GenerateResponse> {
  return request<import("@/types/generation").GenerateResponse>(`/templates/generate/from-template/${id}`, { method: "POST" });
}
