export type QualitySettings = {
  missing_values: number;
  duplicates: number;
  outliers: number;
  invalid_formats: number;
  referential_noise: number;
};

export type GenerateRequest = {
  industry: string;
  scenario: string;
  configuration: Record<string, number>;
  export: "zip";
  quality: QualitySettings;
};

export type GenerateResponse = {
  download_url: string;
  generated_files: string[];
  row_counts: Record<string, number>;
  generated_at: string;
  scenario: string;
  quality: QualitySettings;
  challenge_title: string;
  difficulty: string;
  estimated_time: string;
  challenge_pdf_url: string;
};
