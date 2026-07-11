"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { cloneHistoryEntry, clearHistory, deleteHistoryEntry, fetchHistory, fetchHistoryEntry, regenerateHistoryEntry } from "@/services/history-service";

export function useHistory() {
  return useQuery({ queryKey: ["history"], queryFn: fetchHistory });
}

export function useHistoryEntry(id: string) {
  return useQuery({ queryKey: ["history", id], queryFn: () => fetchHistoryEntry(id), enabled: Boolean(id) });
}

export function useDeleteHistoryEntry() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deleteHistoryEntry(id),
    onSuccess: () => client.invalidateQueries({ queryKey: ["history"] }),
  });
}

export function useClearHistory() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: () => clearHistory(),
    onSuccess: () => client.invalidateQueries({ queryKey: ["history"] }),
  });
}

export function useRegenerateHistoryEntry() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => regenerateHistoryEntry(id),
    onSuccess: () => client.invalidateQueries({ queryKey: ["history"] }),
  });
}

export function useCloneHistoryEntry() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => cloneHistoryEntry(id),
    onSuccess: () => client.invalidateQueries({ queryKey: ["history"] }),
  });
}
