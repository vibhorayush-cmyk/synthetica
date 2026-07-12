import type { HistoryEntry } from "@/types/history";
import { apiRequest } from "@/services/api-client";

export async function fetchHistory(): Promise<HistoryEntry[]> {
  return apiRequest<HistoryEntry[]>("/history");
}

export async function fetchHistoryEntry(id: string): Promise<HistoryEntry> {
  return apiRequest<HistoryEntry>(`/history/${id}`);
}

export async function deleteHistoryEntry(id: string): Promise<void> {
  await apiRequest<void>(`/history/${id}`, { method: "DELETE" });
}

export async function clearHistory(): Promise<void> {
  await apiRequest<void>("/history", { method: "DELETE" });
}

export async function regenerateHistoryEntry(id: string): Promise<HistoryEntry> {
  return apiRequest<HistoryEntry>(`/history/${id}/regenerate`, { method: "POST" });
}

export async function cloneHistoryEntry(id: string): Promise<HistoryEntry> {
  return apiRequest<HistoryEntry>(`/history/${id}/clone`, { method: "POST" });
}
