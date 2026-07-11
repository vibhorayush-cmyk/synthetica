import type { HistoryEntry } from "@/types/history";

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

export async function fetchHistory(): Promise<HistoryEntry[]> {
  return request<HistoryEntry[]>("/history");
}

export async function fetchHistoryEntry(id: string): Promise<HistoryEntry> {
  return request<HistoryEntry>(`/history/${id}`);
}

export async function deleteHistoryEntry(id: string): Promise<void> {
  await request<void>(`/history/${id}`, { method: "DELETE" });
}

export async function clearHistory(): Promise<void> {
  await request<void>("/history", { method: "DELETE" });
}

export async function regenerateHistoryEntry(id: string): Promise<HistoryEntry> {
  return request<HistoryEntry>(`/history/${id}/regenerate`, { method: "POST" });
}

export async function cloneHistoryEntry(id: string): Promise<HistoryEntry> {
  return request<HistoryEntry>(`/history/${id}/clone`, { method: "POST" });
}
