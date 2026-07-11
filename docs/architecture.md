# Architecture

## System overview

Synthetica has a Next.js frontend, FastAPI API, industry plugin registry, and
in-process Pandas generation pipeline. Templates and history currently use
JSON-backed repositories. The export layer writes a local bundle and ZIP file.

```mermaid
flowchart LR
  User --> Web[Next.js Frontend]
  Web --> API[FastAPI API]
  API --> Service[Generation Service]
  Service --> Registry[Industry Plugin Registry]
  Registry --> Plugin[Industry Plugin]
  Plugin --> Generator[Dataset Generator]
  Generator --> Scenario[Scenario Engine]
  Scenario --> Quality[Data Quality Engine]
  Quality --> Challenge[Challenge Engine]
  Challenge --> Export[Export Service]
  Export --> Zip[ZIP Download]
```

## Backend components

```mermaid
flowchart TB
  Routes[API routes] --> Services[Services]
  Services --> Plugins[Plugins]
  Plugins --> Scenarios[Scenarios]
  Plugins --> Quality[Data quality]
  Plugins --> Challenges[Challenges]
  Services --> Exporters[Exporters]
  Routes --> Templates[Templates]
  Routes --> History[History]
  Schema[Schema designer helpers] --> Services
```

## Frontend architecture

The App Router provides the public landing page, `/workspace`, templates,
history, and schema designer pages. Reusable components provide application
shells, forms, brand assets, cards, and summaries. Hooks use TanStack Query for
remote state; services wrap API calls; types describe API contracts; React Hook
Form and Zod validate workspace input.

## Plugin lifecycle

1. Plugins are discovered and registered.
2. The frontend loads plugin metadata from `/industries`.
3. The user submits a configuration map for a selected plugin.
4. The plugin validates configuration and generates tables.
5. A scenario and quality rules modify those tables.
6. A challenge pack is generated.
7. Exporters create the downloadable bundle.

## Data generation sequence

```mermaid
sequenceDiagram
  participant F as Frontend
  participant A as API
  participant S as GenerationService
  participant R as PluginRegistry
  participant P as IndustryPlugin
  participant SE as ScenarioEngine
  participant QE as QualityEngine
  participant CE as ChallengeEngine
  participant E as ExportService
  F->>A: POST /generate
  A->>S: validated request
  S->>R: resolve industry
  R-->>S: plugin
  S->>P: generate configuration
  P->>SE: apply scenario
  SE->>QE: apply quality rules
  QE->>CE: generate challenge
  CE->>E: export bundle
  E-->>A: result metadata
  A-->>F: download URL
```

## Data model examples

### Retail

```mermaid
erDiagram
  CUSTOMERS ||--o{ ORDERS : places
  STORES ||--o{ ORDERS : fulfills
  ORDERS ||--o{ ORDER_ITEMS : contains
  PRODUCTS ||--o{ ORDER_ITEMS : appears_in
```

### Banking

```mermaid
erDiagram
  CUSTOMERS ||--o{ ACCOUNTS : owns
  CUSTOMERS ||--o{ LOANS : borrows
  CUSTOMERS ||--o{ CREDIT_CARDS : holds
  BRANCHES ||--o{ ACCOUNTS : manages
  ACCOUNTS ||--o{ TRANSACTIONS : records
  CREDIT_CARDS ||--o{ PAYMENTS : receives
```

## Configuration flow

`app.core.settings.Settings` loads `.env` values. Current settings include
`EXPORT_DIR`, `CORS_ORIGINS`, `MAX_DATASET_ROWS`, API prefix, rate limits, and
local template/history directories. The frontend reads `NEXT_PUBLIC_API_URL`.
`API URL` is a deployment concept rather than a backend setting name.

## Error handling

Pydantic returns validation errors for invalid payloads. Plugin validation
rejects unsupported industries or scenarios. Download routes return `404` for
missing files or invalid paths. Export and plugin failures are logged and
surface as API failures; plugin discovery failures prevent the affected plugin
from being available.

## Security considerations

Inputs and row limits are validated. Download routes allow ZIP files and a
specific challenge PDF only, resolve paths beneath the export root, and reject
traversal attempts. CORS is configured from settings. Local exports are
temporary/demo-friendly storage; public deployments should restrict access,
manage retention, and use durable object storage.

## Scalability

Current generation is Pandas in-memory, exports use the local filesystem, and
templates/history are JSON-backed. Planned production options include
PostgreSQL, object storage, background jobs, Redis, Celery or RQ, and
horizontally scaled API workers.
