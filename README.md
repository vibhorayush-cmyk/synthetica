# Synthetica

> **Realistic data. Real analytical practice.**

Synthetica is a production-oriented synthetic analytics platform for building
industry-aware datasets, practising analytical workflows, and assembling
portfolio-ready projects. It combines a Next.js workspace with a FastAPI data
pipeline that produces documented ZIP bundles rather than isolated random rows.

![Build status placeholder](https://img.shields.io/badge/build-workflow%20not%20configured-lightgrey)
![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?logo=nextdotjs)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2-150458?logo=pandas&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-tested-0A9EDC?logo=pytest&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-deployment%20planned-2496ED?logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**Links:** [Architecture](docs/architecture.md) · [API](docs/api.md) ·
[Plugins](docs/plugins.md) · [Development](docs/development.md) ·
[Deployment](docs/deployment.md) · [Brand](docs/brand.md) ·
[Live demo — placeholder](#) · [API docs — local](http://localhost:8000/api/v1/docs)

## Overview

Synthetica creates realistic practice data for Power BI, SQL, Tableau, Excel,
Python, machine learning, data cleaning, and analytics interview preparation.
Unlike a basic random-data generator, it applies industry-aware schemas, valid
relationships, business scenarios, intentional data-quality issues, and a
professional learning pack to the same generated dataset.

It includes reusable templates, generation history, a plugin architecture, a
visual schema designer, API documentation, and downloadable ZIP bundles.

## Screenshots

Screenshots are repository placeholders until captured from a running local app.

| View | Placeholder |
| --- | --- |
| Landing page | `docs/images/landing-page.png` *(placeholder; not committed yet)* |
| Generation workspace | `docs/images/workspace.png` *(placeholder; not committed yet)* |
| Templates | `docs/images/templates.png` *(placeholder; not committed yet)* |
| History | `docs/images/history.png` *(placeholder; not committed yet)* |
| Schema designer | `docs/images/schema-designer.png` *(placeholder; not committed yet)* |
| Dataset result summary | `docs/images/dataset-result.png` *(placeholder; not committed yet)* |

## Core features

| Capability | What it provides |
| --- | --- |
| Retail and Banking plugins | Industry-specific configuration, schemas, scenarios, and metadata |
| Scenario engine | Business events such as promotions, seasonality, fraud, and recession effects |
| Data-quality engine | Optional missing values, duplicates, outliers, format issues, and referential noise |
| Export service | CSV tables, Excel data dictionary, README, challenge artifacts, and ZIP packaging |
| Challenge and learning packs | Case studies, tasks, requirements, and PDF challenge material |
| Dataset templates | JSON-backed saved configurations and generate-from-template workflow |
| Generation history | JSON-backed history entries with clone, regenerate, download, and delete actions |
| Plugin SDK | Discovery, registration, validation, metadata, and generation contracts |
| Schema designer | Browser-based schema composition and JSON preview |
| Frontend workspace | Metadata-driven Next.js configuration experience |
| API documentation | OpenAPI/Swagger at the configured API prefix |

## Supported industries

| Industry | Status |
| --- | --- |
| Retail | Available |
| Banking | Available |
| Healthcare | Planned |
| Supply Chain | Planned |
| Human Resources | Planned |
| Manufacturing | Planned |

## Generation flow

```text
User Configuration
        → Industry Plugin
        → Dataset Generator
        → Scenario Engine
        → Data Quality Engine
        → Challenge Engine
        → Export Service
        → Downloadable ZIP
```

## Example dataset bundle

```text
Retail_20260712_143045.zip
└── Retail_20260712_143045/
    ├── customers.csv
    ├── products.csv
    ├── stores.csv
    ├── orders.csv
    ├── order_items.csv
    ├── data_dictionary.xlsx
    ├── README.md
    ├── challenge.md
    ├── challenge.pdf
    ├── requirements.md
    └── dataset_overview.md
```

Generated files vary by industry and configuration. Challenge materials include
SQL, Power BI, Excel, Python, Tableau, and machine-learning tasks inside the
challenge pack; they are not currently emitted as separate `sql_questions.md`
or `powerbi_tasks.md` files.

## Technology stack

| Area | Technologies |
| --- | --- |
| Frontend | Next.js, React, TypeScript, Tailwind CSS, TanStack Query, React Hook Form, Zod |
| Backend | FastAPI, Pydantic, Pandas, NumPy, Faker, OpenPyXL |
| Testing | Pytest, TypeScript typecheck, frontend production build |
| Deployment direction | Docker, Vercel, Render or Railway *(planned)* |

## Project structure

```text
app/                    FastAPI application and domain packages
  api/                  HTTP routes and router composition
  plugins/              Industry plugin discovery and implementations
  scenarios/            Business-event transformations
  data_quality/         Intentional quality-rule engine
  exporters/            CSV, Excel, ZIP, and documentation export
  challenges/           Learning-pack generation and rendering
  templates/            JSON-backed dataset template management
  history/              JSON-backed generation history
  schema_designer/      Schema parsing, validation, and generation helpers
  services/             Generation orchestration
frontend/               Next.js App Router application
docs/                   Project documentation
tests/                  Backend tests
requirements.txt        Python dependencies
README.md               Repository overview
```

## Quick start

### Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

- Frontend: <http://localhost:3000>
- Backend: <http://localhost:8000>
- Swagger: <http://localhost:8000/api/v1/docs>

## Example API requests

### Retail

```bash
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "industry": "retail",
    "scenario": "black_friday",
    "configuration": {
      "customers": 10000,
      "products": 500,
      "stores": 50,
      "orders": 100000
    },
    "export": "zip",
    "quality": {"missing_values": 5, "duplicates": 2, "outliers": 1}
  }'
```

### Banking

```bash
curl -X POST http://localhost:8000/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "industry": "banking",
    "scenario": "fraud_spike",
    "configuration": {
      "customers": 10000,
      "accounts": 15000,
      "transactions": 100000,
      "loans": 5000,
      "branches": 20,
      "credit_cards": 4000
    },
    "export": "zip",
    "quality": {"outliers": 1, "referential_noise": 0}
  }'
```

## Testing

```bash
# Backend (root directory)
python -m pytest

# Frontend
cd frontend
npm run typecheck
npm run build
```

## Plugin development

New industries are added through the plugin architecture: implement the plugin
contract, provide metadata and configuration validation, then register or make
it discoverable. See [Plugin development](docs/plugins.md).

## Documentation

- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)
- [Plugin guide](docs/plugins.md)
- [Development guide](docs/development.md)
- [Deployment guide](docs/deployment.md)
- [Brand system](docs/brand.md)

## Roadmap

**Completed:** Retail, Banking, templates, history, scenario engine,
data-quality engine, schema designer, challenge packs, plugin framework, and
frontend workspace.

**Planned:** Docker deployment, cloud deployment, PostgreSQL persistence,
object storage, authentication, Healthcare, Supply Chain, and AI schema
generation.

## Contributing

Contributions are welcome. Review [CONTRIBUTING.md](CONTRIBUTING.md) for setup,
testing, pull request expectations, and the plugin contribution process.

## License

Synthetica is available under the [MIT License](LICENSE).
