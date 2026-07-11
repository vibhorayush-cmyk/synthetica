import { z } from "zod";

export const templateSchema = z.object({
  name: z.string().trim().min(1, "Name is required"),
  description: z.string().trim().min(1, "Description is required"),
  industry: z.literal("retail"),
  scenario: z.enum(["none", "black_friday", "christmas", "summer_sale", "recession"]),
  customers: z.coerce.number().int().min(1, "Customers must be at least 1"),
  products: z.coerce.number().int().min(1, "Products must be at least 1"),
  stores: z.coerce.number().int().min(1, "Stores must be at least 1"),
  orders: z.coerce.number().int().min(1, "Orders must be at least 1"),
  export_type: z.string().trim().min(1, "Export type is required"),
  quality: z.object({
    missing_values: z.coerce.number().min(0).max(100),
    duplicates: z.coerce.number().min(0).max(100),
    outliers: z.coerce.number().min(0).max(100),
    invalid_formats: z.coerce.number().min(0).max(100),
    referential_noise: z.coerce.number().min(0).max(100),
  }),
  difficulty: z.enum(["Beginner", "Intermediate", "Advanced"]),
});

export type TemplateFormSchema = z.infer<typeof templateSchema>;
