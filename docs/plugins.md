# Plugin Development Guide

Synthetica uses industry plugins to keep domain-specific generation logic out
of the core API and frontend. A plugin owns its schema, supported scenarios,
quality registry, configuration validation, challenge context, and frontend
metadata.

## Current plugins

- `retail` — available
- `banking` — available
- `healthcare` — metadata placeholder; generation is planned

## Contract

Implement `BaseIndustryPlugin` in `app/plugins/<industry>/plugin.py`. A plugin
provides an identifier, name, description, version, supported scenarios and
quality rules, templates, defaults, validation, generation, and frontend
metadata.

```text
app/plugins/
  base.py
  interfaces.py
  loader.py
  registry.py
  retail/plugin.py
  banking/plugin.py
```

## Lifecycle

1. `loader.py` discovers plugin implementations.
2. `PluginRegistry` registers plugins by ID.
3. `/industries` exposes `frontend_metadata()` to the Next.js workspace.
4. The frontend submits the selected `configuration` map to `POST /generate`.
5. `GenerationService` resolves the plugin and delegates generation.
6. The plugin applies its scenario and quality engines, creates a challenge,
   and passes tables to the export service.

## Frontend metadata

`frontend_metadata()` should describe the plugin without requiring
industry-specific React conditions. Include configuration fields, field layout,
supported scenarios, templates, KPIs, dashboard suggestions, challenge types,
icon, color, and `generation_available`.

## Contribution checklist

- Add a self-contained plugin package.
- Validate all configuration fields and supported names.
- Preserve relationships after scenarios and quality rules.
- Add tests for table shape, foreign keys, metadata, and export behavior.
- Update [README](../README.md), [API docs](api.md), and supported-industry
  status when appropriate.
