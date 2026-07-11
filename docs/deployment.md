# Deployment Guide

> Deployment is planned; this document describes the intended architecture and
> does not claim a completed production deployment.

## Intended architecture

| Component | Demo / MVP | Production direction |
| --- | --- | --- |
| Frontend | Local Next.js | Vercel |
| Backend | Local FastAPI | Render or Railway |
| Generated files | Temporary local storage | Object storage |
| Persistence | JSON/local storage | PostgreSQL |

## Production checklist

- [ ] Set a strong `SECRET_KEY`.
- [ ] Set explicit `CORS_ORIGINS` for the frontend domain.
- [ ] Set a durable `EXPORT_DIR` or object-storage integration.
- [ ] Set `MAX_DATASET_ROWS` appropriate for available worker memory.
- [ ] Use managed PostgreSQL before multi-instance deployment.
- [ ] Add retention and cleanup policy for generated files.
- [ ] Configure HTTPS, monitoring, logs, and error reporting.
- [ ] Move long-running generation to background workers before high-volume use.

## Planned improvements

Object storage, PostgreSQL, authentication, background jobs, Redis, and
worker queues are planned production extensions. Vercel is suited to the
frontend; Render or Railway are candidate backend hosts.
