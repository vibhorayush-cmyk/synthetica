# Synthetic Analytics Frontend

Next.js 15 dashboard for the Synthetic Analytics FastAPI service.

## Run locally

```bash
cp .env.local.example .env.local
npm install
npm run dev
```

The frontend uses `NEXT_PUBLIC_API_URL`, which defaults to
`http://localhost:8000` when unset. Start the FastAPI backend on that address
before generating a dataset.
