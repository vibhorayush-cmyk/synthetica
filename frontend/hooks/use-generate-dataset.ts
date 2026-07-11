import { useMutation } from "@tanstack/react-query";
import { generateDataset } from "@/services/generation-service";

export function useGenerateDataset() {
  return useMutation({ mutationFn: generateDataset });
}
