"use client";

import { useMemo, useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import { ThemeToggle } from "@/components/theme-toggle";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const fieldTypes = ["text", "integer", "decimal", "boolean", "date", "timestamp", "enum", "currency", "email", "phone", "address", "country", "foreign_key", "primary_key", "uuid"];

type ColumnModel = {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
  default?: string | number | boolean | null;
  min_value?: number;
  max_value?: number;
  enum_values?: string[];
};

type TableModel = {
  name: string;
  rows: number;
  columns: ColumnModel[];
};

const starterSchema: { tables: TableModel[] } = {
  tables: [
    {
      name: "Customers",
      rows: 1000,
      columns: [
        { name: "CustomerID", type: "primary_key", primary_key: true, nullable: false },
        { name: "Name", type: "text", primary_key: false, nullable: false },
        { name: "Email", type: "email", primary_key: false, nullable: false },
      ],
    },
    {
      name: "Orders",
      rows: 2000,
      columns: [
        { name: "OrderID", type: "primary_key", primary_key: true, nullable: false },
        { name: "CustomerID", type: "foreign_key", primary_key: false, nullable: false, default: "Customers" },
        { name: "Amount", type: "decimal", primary_key: false, nullable: false },
      ],
    },
  ],
};

export default function SchemaDesignerPage() {
  const [schema, setSchema] = useState<{ tables: TableModel[] }>(starterSchema);
  const [selectedTable, setSelectedTable] = useState("Customers");
  const [jsonPreview, setJsonPreview] = useState(JSON.stringify(starterSchema, null, 2));

  const tables = schema.tables;
  const tableCount = tables.length;
  const relationshipCount = tables.reduce((sum, table) => sum + table.columns.filter((column) => column.type === "foreign_key").length, 0);
  const estimatedRowCount = tables.reduce((sum, table) => sum + table.rows, 0);
  const estimatedExportSize = estimatedRowCount * 0.5;

  const updateSchema = (next: typeof schema) => {
    setSchema(next);
    setJsonPreview(JSON.stringify(next, null, 2));
  };

  const currentTable = useMemo(() => tables.find((table) => table.name === selectedTable) ?? tables[0], [selectedTable, tables]);

  return (
    <main className="min-h-screen lg:grid lg:grid-cols-[250px_1fr_320px]">
      <AppSidebar />
      <section className="min-w-0 px-4 py-6 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-6xl space-y-6">
          <header className="flex items-start justify-between gap-4">
            <div>
              <p className="mb-2 text-sm font-medium text-brand-600">Designer</p>
              <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Visual Schema Designer</h1>
              <p className="mt-3 max-w-3xl text-slate-600 dark:text-slate-400">Compose custom datasets visually and export them as JSON for generation and analysis.</p>
            </div>
            <ThemeToggle />
          </header>

          <div className="grid gap-4 lg:grid-cols-[220px_minmax(0,1fr)]">
            <Card className="p-4">
              <h2 className="text-lg font-semibold">Field Types</h2>
              <div className="mt-4 space-y-2">
                {fieldTypes.map((fieldType) => (
                  <div key={fieldType} className="rounded-lg border border-slate-200 px-3 py-2 text-sm dark:border-slate-800">
                    {fieldType}
                  </div>
                ))}
              </div>
            </Card>
            <div className="space-y-4">
              <Card className="p-4">
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-semibold">Tables</h2>
                    <p className="text-sm text-slate-500">Create, rename, and edit custom tables.</p>
                  </div>
                  <Button onClick={() => updateSchema({ tables: [...tables, { name: `Table${tables.length + 1}`, rows: 100, columns: [] }] })}>Create Table</Button>
                </div>
                <div className="mt-4 grid gap-3 md:grid-cols-2">
                  {tables.map((table) => (
                    <button key={table.name} type="button" className={`rounded-xl border px-4 py-3 text-left ${selectedTable === table.name ? "border-brand-500 bg-brand-50 dark:bg-brand-500/10" : "border-slate-200 dark:border-slate-800"}`} onClick={() => setSelectedTable(table.name)}>
                      <p className="font-semibold">{table.name}</p>
                      <p className="mt-1 text-sm text-slate-500">{table.columns.length} columns · {table.rows} rows</p>
                    </button>
                  ))}
                </div>
              </Card>

              {currentTable ? (
                <Card className="p-4">
                  <div className="flex items-center justify-between gap-3">
                    <h3 className="text-lg font-semibold">{currentTable.name}</h3>
                    <div className="flex gap-2">
                      <Button variant="secondary" onClick={() => setSelectedTable(tables[0]?.name ?? "")}>Focus</Button>
                      <Button variant="secondary" onClick={() => updateSchema({ tables: tables.filter((table) => table.name !== currentTable.name) })}>Delete</Button>
                    </div>
                  </div>
                  <div className="mt-4 space-y-3">
                    {currentTable.columns.map((column, index) => (
                      <div key={`${column.name}-${index}`} className="rounded-xl border border-slate-200 p-3 dark:border-slate-800">
                        <div className="flex items-center justify-between gap-2">
                          <p className="font-medium">{column.name}</p>
                          <select className="input" value={column.type} onChange={(event) => {
                            const next = tables.map((table) => table.name === currentTable.name ? { ...table, columns: table.columns.map((item, itemIndex) => itemIndex === index ? { ...item, type: event.target.value } : item) } : table);
                            updateSchema({ tables: next });
                          }}>
                            {fieldTypes.map((fieldType) => <option key={fieldType} value={fieldType}>{fieldType}</option>)}
                          </select>
                        </div>
                        <div className="mt-3 grid gap-3 sm:grid-cols-2">
                          <label className="text-sm text-slate-600 dark:text-slate-400"><span className="mb-1 block">Primary Key</span><input type="checkbox" checked={column.primary_key} onChange={(event) => { const next = tables.map((table) => table.name === currentTable.name ? { ...table, columns: table.columns.map((item, itemIndex) => itemIndex === index ? { ...item, primary_key: event.target.checked } : item) } : table); updateSchema({ tables: next }); }} /></label>
                          <label className="text-sm text-slate-600 dark:text-slate-400"><span className="mb-1 block">Nullable</span><input type="checkbox" checked={column.nullable} onChange={(event) => { const next = tables.map((table) => table.name === currentTable.name ? { ...table, columns: table.columns.map((item, itemIndex) => itemIndex === index ? { ...item, nullable: event.target.checked } : item) } : table); updateSchema({ tables: next }); }} /></label>
                        </div>
                      </div>
                    ))}
                    <Button variant="secondary" onClick={() => {
                      const next = tables.map((table) => table.name === currentTable.name ? { ...table, columns: [...table.columns, { name: `Column${table.columns.length + 1}`, type: "text", primary_key: false, nullable: true }] } : table);
                      updateSchema({ tables: next });
                    }}>Add Column</Button>
                  </div>
                </Card>
              ) : null}
            </div>
          </div>
        </div>
      </section>
      <aside className="border-t border-slate-200 px-4 py-6 dark:border-slate-800 lg:border-l lg:px-5">
        <div className="space-y-4">
          <Card className="p-4">
            <h2 className="text-lg font-semibold">Preview</h2>
            <div className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-400">
              <div>Tables: {tableCount}</div>
              <div>Relationships: {relationshipCount}</div>
              <div>Estimated row count: {estimatedRowCount}</div>
              <div>Estimated export size: {estimatedExportSize.toFixed(1)} MB</div>
            </div>
          </Card>
          <Card className="p-4">
            <h2 className="text-lg font-semibold">JSON Preview</h2>
            <pre className="mt-3 overflow-auto text-xs text-slate-600 dark:text-slate-400">{jsonPreview}</pre>
          </Card>
        </div>
      </aside>
    </main>
  );
}
