# Developer Guide

Install backend tooling with `pip install -r requirements-dev.txt` and frontend tooling with `cd frontend && npm ci`.

Run quality checks:

```bash
ruff check app tests
black app tests
pytest
cd frontend && npm run typecheck && npm run build
```

Use `.env.example` as the starting point for local configuration. Never commit `.env`.
