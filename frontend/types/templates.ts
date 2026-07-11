export type TemplateQuality = {
  missing_values: number;
  duplicates: number;
  outliers: number;
  invalid_formats: number;
  referential_noise: number;
};

export type TemplateRecord = {
  id: string;
  name: string;
  description: string;
  industry: "retail";
  scenario: "none" | "black_friday" | "christmas" | "summer_sale" | "recession";
  customers: number;
  products: number;
  stores: number;
  orders: number;
  export_type: string;
  quality: TemplateQuality;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  created_at: string;
  updated_at: string;
  version: number;
};

export type TemplateFormValues = {
  name: string;
  description: string;
  industry: "retail";
  scenario: "none" | "black_friday" | "christmas" | "summer_sale" | "recession";
  customers: number;
  products: number;
  stores: number;
  orders: number;
  export_type: string;
  quality: TemplateQuality;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
};
