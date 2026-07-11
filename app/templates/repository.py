"""Repository abstraction for storing templates as JSON files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from app.config import BASE_DIR
from app.templates.models import TemplateModel


class TemplateRepository(Protocol):
    """Storage abstraction for templates."""

    def list(self) -> list[TemplateModel]:
        """Return all templates."""

    def get(self, template_id: str) -> TemplateModel:
        """Return one template."""

    def create(self, template: TemplateModel) -> TemplateModel:
        """Persist a new template."""

    def update(self, template: TemplateModel) -> TemplateModel:
        """Persist an updated template."""

    def delete(self, template_id: str) -> None:
        """Remove a template."""


class JsonTemplateRepository:
    """Store templates as JSON files in a directory."""

    def __init__(self, storage_dir: Path | None = None) -> None:
        self._storage_dir = storage_dir or BASE_DIR / "templates"
        self._storage_dir.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[TemplateModel]:
        templates: list[TemplateModel] = []
        for file_path in sorted(self._storage_dir.glob("*.json")):
            templates.append(self._load(file_path))
        return templates

    def get(self, template_id: str) -> TemplateModel:
        file_path = self._storage_dir / f"{template_id}.json"
        if not file_path.exists():
            raise ValueError(f"template not found: {template_id}")
        return self._load(file_path)

    def create(self, template: TemplateModel) -> TemplateModel:
        self._save(template)
        return template

    def update(self, template: TemplateModel) -> TemplateModel:
        self._save(template)
        return template

    def delete(self, template_id: str) -> None:
        file_path = self._storage_dir / f"{template_id}.json"
        if file_path.exists():
            file_path.unlink()

    def _save(self, template: TemplateModel) -> None:
        payload = template.to_payload()
        file_path = self._storage_dir / f"{template.id}.json"
        file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _load(self, file_path: Path) -> TemplateModel:
        payload = json.loads(file_path.read_text(encoding="utf-8"))
        return TemplateModel(**payload)


def build_template_id() -> str:
    """Create a stable, URL-safe template identifier."""
    return uuid4().hex
