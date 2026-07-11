# API Reference

The local API base URL is `http://localhost:8000`. The application also mounts
the same routes under the configured `/api/v1` prefix; Swagger is available at
`/api/v1/docs`. Examples below use unversioned local paths.

## Service endpoints

### `GET /`

Returns basic service identity and readiness.

```json
{"service":"synthetic-analytics-data-generator","status":"ready"}
```

Errors: `429` when rate limits are exceeded.

### `GET /health`

Returns a lightweight liveness response.

```json
{"status":"healthy"}
```

Related current endpoints: `GET /ready`, `GET /readyz`, and `GET /metrics`.

## Industry metadata

### `GET /industries`

Returns discoverable plugin contracts used by the metadata-driven frontend.

```json
[{"id":"retail","name":"Retail","status":"available","configuration_fields":[{"key":"customers","type":"number","default":10000}]}]
```

Errors: `429` when rate-limited.

### `GET /industries/{industry}`

Returns one plugin contract, including configuration fields, scenarios, KPIs,
templates, challenge types, and layout metadata.

```text
GET /industries/retail
```

Errors: `404` for an unknown industry; `429` when rate-limited.

## Dataset generation

### `POST /generate`

Generates a plugin dataset, applies scenario and quality settings, writes a ZIP
bundle, and returns its metadata.

```json
{
  "industry": "retail",
  "scenario": "black_friday",
  "configuration": {
    "customers": 10000,
    "products": 500,
    "stores": 50,
    "orders": 100000
  },
  "export": "zip",
  "quality": {
    "missing_values": 5,
    "duplicates": 2,
    "outliers": 1,
    "invalid_formats": 0,
    "referential_noise": 0
  }
}
```

Example response:

```json
{
  "download_url": "http://localhost:8000/downloads/Retail_20260712_143045.zip",
  "generated_files": ["customers.csv", "data_dictionary.xlsx", "challenge.pdf"],
  "row_counts": {"customers": 10000, "orders": 100000},
  "generated_at": "2026-07-12T14:30:45",
  "scenario": "black_friday",
  "quality": {"missing_values": 5, "duplicates": 2, "outliers": 1, "invalid_formats": 0, "referential_noise": 0},
  "challenge_title": "Retail Performance Investigation",
  "difficulty": "Advanced",
  "estimated_time": "10–14 hours",
  "challenge_pdf_url": "http://localhost:8000/downloads/Retail_20260712_143045/challenge.pdf"
}
```

Errors: `422` for invalid configuration, unknown plugin/scenario, or values
above `MAX_DATASET_ROWS`; `429` when rate-limited; `500` for unexpected export
or plugin failures.

## Downloads

### `GET /downloads/{filename}`

Downloads a generated ZIP archive. Only a simple `.zip` file name under the
export root is accepted.

```text
GET /downloads/Retail_20260712_143045.zip
```

Errors: `404` for missing archives, invalid extensions, or invalid paths.

### `GET /downloads/{bundle_name}/challenge.pdf`

Downloads the challenge PDF from a generated bundle.

Errors: `404` for a missing bundle, unsupported individual file, or invalid
path.

## Templates

Template endpoints are JSON-backed and mounted at `/templates`.

| Method | Path | Purpose | Errors |
| --- | --- | --- | --- |
| `GET` | `/templates` | List templates | `429` |
| `POST` | `/templates` | Create a template | `422`, `429` |
| `GET` | `/templates/{template_id}` | Read one template | `404`, `429` |
| `PUT` | `/templates/{template_id}` | Update a template | `404`, `429` |
| `DELETE` | `/templates/{template_id}` | Delete a template | `204`, `429` |
| `POST` | `/templates/generate/from-template/{template_id}` | Generate from saved configuration | `404`, `429` |

Create request example:

```json
{"name":"Black Friday retail","description":"Promotion analysis starter","industry":"retail","scenario":"black_friday","customers":10000,"products":500,"stores":50,"orders":100000,"export_type":"zip","quality":{"missing_values":5},"difficulty":"Advanced"}
```

Template responses contain `id`, name/description, industry, scenario, the four
count fields, export type, quality, difficulty, timestamps, and version.
`GET` endpoints have no request body. `PUT /templates/{template_id}` accepts
any subset of the same editable fields. `DELETE` endpoints return no body.
`POST /templates/generate/from-template/{template_id}` has no request body and
returns the same dataset response shape as `POST /generate`.

## History

History endpoints are JSON-backed and mounted at `/history`.

| Method | Path | Purpose | Errors |
| --- | --- | --- | --- |
| `GET` | `/history` | List generation history | `429` |
| `GET` | `/history/{entry_id}` | Read one entry | `404`, `429` |
| `DELETE` | `/history/{entry_id}` | Delete one entry | `204`, `429` |
| `DELETE` | `/history` | Delete all entries | `204`, `429` |
| `POST` | `/history/{entry_id}/regenerate` | Clone an entry for regeneration | `404`, `429` |
| `POST` | `/history/{entry_id}/clone` | Clone an entry | `404`, `429` |

`GET` endpoints have no request body and return history-entry records. A record
includes identifier, dataset name, industry, scenario, timestamps, generation
status, row counts, ZIP file name/size, quality settings, and challenge
metadata. `DELETE` endpoints return no body. Clone/regenerate endpoints have no
request body and return the resulting history-entry record.

## Schema designer

The current schema designer is a frontend route at `/schema-designer`. Its
backend parser, validator, relationship builder, and generator are library
components; no schema-designer HTTP routes are registered in the current API.
