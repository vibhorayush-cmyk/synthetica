export type SchemaDesignerColumn = {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
  default?: string | number | boolean | null;
  min_value?: number;
  max_value?: number;
  enum_values?: string[];
};

export type SchemaDesignerTable = {
  name: string;
  rows: number;
  columns: SchemaDesignerColumn[];
};

export type SchemaDesignerSchema = {
  tables: SchemaDesignerTable[];
};
