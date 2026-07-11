# Deployment Guide

1. Copy `.env.example` to `.env` and replace `SECRET_KEY`.
2. Configure a durable `EXPORT_DIR` and `DATABASE_URL`.
3. Set production `CORS_ORIGINS` explicitly.
4. Run `docker compose up --build`.
5. Use `/ready` for orchestration probes and `/metrics` for monitoring.

For multi-instance deployments, replace the local rate-limit middleware with a shared Redis implementation and store exports in object storage.
