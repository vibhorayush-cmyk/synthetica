# Development Guide

## Prerequisites

- Python 3.12 or newer
- Node.js and npm
- Git

## Backend setup

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Frontend setup

```bash
cd frontend
cp .env.local.example .env.local
npm install
npm run dev
```

## Environment variables

Backend settings are loaded from `.env` through `app.core.settings.Settings`.
Common values include `EXPORT_DIR`, `CORS_ORIGINS`, `MAX_DATASET_ROWS`,
`DATABASE_URL`, `HISTORY_DIR`, `TEMPLATE_DIR`, and `SECRET_KEY`.

The frontend uses `NEXT_PUBLIC_API_URL`; it defaults to
`http://localhost:8000` when unset.

## Verification

```bash
# Backend, from repository root
python -m pytest

# Frontend
cd frontend
npm test
npm run typecheck
npm run build
```

## Extending the platform

- **Plugin:** implement `BaseIndustryPlugin`, provide metadata and validation,
  and make the module discoverable under `app/plugins`.
- **Scenario:** implement `BaseScenario`, register it for an industry, and keep
  generated foreign keys and totals consistent.
- **Quality rule:** implement `BaseQualityRule`, register it with the industry
  quality registry, and avoid modifying primary keys unless that rule explicitly
  documents its behavior.
- **Template:** extend template schemas, repository, and service together.

See [Plugin guide](plugins.md) for the full plugin lifecycle.

## Troubleshooting

- **Frontend is unstyled:** restart `npm run dev` after a production build; a
  dev process can hold stale Next.js asset paths.
- **Workspace has incomplete fields:** verify `GET /industries` returns full
  plugin metadata and restart an older API process.
- **Generation is rejected:** check scenario support, configuration values, and
  the `MAX_DATASET_ROWS` setting.
- **Download returns 404:** confirm the generated bundle still exists beneath
  `EXPORT_DIR`.
