import { useQuery } from "@tanstack/react-query";
import type { IndustryPlugin } from "@/types/industry";

const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function useIndustries() {
  return useQuery<IndustryPlugin[]>({
    queryKey: ["industries"],
    queryFn: async () => {
      const response = await fetch(`${apiUrl}/industries`);
      if (!response.ok) {
        throw new Error("Failed to load industries");
      }
      return response.json() as Promise<IndustryPlugin[]>;
    },
  });
}
