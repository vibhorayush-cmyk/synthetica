import { z } from "zod";

const percentage = z.coerce.number().min(0).max(100);
const count = z.coerce.number().int().min(1).max(1_000_000);

export const datasetSchema = z.object({
  industry: z.string().min(1),
  scenario: z.string().min(1),
  configuration: z.record(z.string(), count),
  export: z.literal("zip"),
  quality: z.object({
    missing_values: percentage,
    duplicates: percentage,
    outliers: percentage,
    invalid_formats: percentage,
    referential_noise: percentage,
  }),
});

export type DatasetFormValues = z.infer<typeof datasetSchema>;
