"""Top-level API router."""

from fastapi import APIRouter

from app.api.routes import auth, generation, health, industries, root, users
from app.history.routes import router as history_router
from app.templates.routes import router as templates_router


api_router = APIRouter()
api_router.include_router(root.router)
api_router.include_router(health.router)
api_router.include_router(industries.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(generation.router)
api_router.include_router(templates_router)
api_router.include_router(history_router)
