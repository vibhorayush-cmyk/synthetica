export type ConfigurationField = {
  key: string;
  label: string;
  type: "number";
  default: number;
  minimum: number;
  maximum: number;
  help_text?: string;
};

export type FieldLayoutSection = {
  title: string;
  fields: string[];
  columns: number;
};

export type IndustryPlugin = {
  id: string;
  name: string;
  description: string;
  version: string;
  status: "available" | "coming_soon";
  icon: string;
  color: string;
  configuration_fields: ConfigurationField[];
  supported_scenarios: string[];
  supported_templates: Array<{ name?: string } | string>;
  kpis: string[];
  dashboard_suggestions: string[];
  challenge_types: string[];
  field_layout: FieldLayoutSection[];
  generation_available: boolean;
};
