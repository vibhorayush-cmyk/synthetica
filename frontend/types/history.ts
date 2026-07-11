export type HistoryStatus = "completed" | "failed" | "in_progress";

export type HistoryEntry = {
  id: string;
  dataset_name: string;
  industry: string;
  scenario: string;
  template_name: string | null;
  quality: Record<string, number>;
  customers: number;
  products: number;
  stores: number;
  orders: number;
  export_type: string;
  zip_filename: string;
  zip_size: number;
  generated_at: string;
  generation_duration_ms: number;
  status: HistoryStatus;
  challenge_title: string | null;
  generated_files: string[];
  readme_preview: string | null;
  data_dictionary_preview: string | null;
};
