"""Application service for managing dataset templates."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Mapping

from pathlib import Path

from app.models.generation import GenerateRequest, GenerateResponse, ExportFormat
from app.services.generation_service import GenerationService, get_generation_service
from app.templates.models import TemplateModel
from app.templates.repository import TemplateRepository, build_template_id
from app.templates.schemas import TemplateCreate, TemplateUpdate


class TemplateService:
    """Coordinate template CRUD and generation from template."""

    def __init__(
        self,
        repository: TemplateRepository,
        generation_service: GenerationService | None = None,
    ) -> None:
        self._repository = repository
        self._generation_service = generation_service or get_generation_service()

    def list_templates(self) -> list[TemplateModel]:
        """Return all persisted templates."""
        return self._repository.list()

    def get_template(self, template_id: str) -> TemplateModel:
        """Return one template by id."""
        return self._repository.get(template_id)

    def create_template(self, payload: TemplateCreate) -> TemplateModel:
        """Create and persist a new template."""
        self._validate_name_is_unique(payload.name)
        self._validate_payload(payload)
        template = TemplateModel(
            id=build_template_id(),
            name=payload.name,
            description=payload.description,
            industry=payload.industry,
            scenario=payload.scenario,
            customers=payload.customers,
            products=payload.products,
            stores=payload.stores,
            orders=payload.orders,
            export_type=payload.export_type,
            quality=payload.quality,
            difficulty=payload.difficulty,
        )
        return self._repository.create(template)

    def update_template(
        self, template_id: str, payload: TemplateUpdate
    ) -> TemplateModel:
        """Update an existing template."""
        existing = self.get_template(template_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "name" in update_data and update_data["name"] != existing.name:
            self._validate_name_is_unique(update_data["name"])
        merged = TemplateModel(**existing.to_payload())
        for key, value in update_data.items():
            setattr(merged, key, value)
        merged.updated_at = datetime.now(timezone.utc)
        merged.version = existing.version + 1
        self._validate_payload(merged)
        return self._repository.update(merged)

    def delete_template(self, template_id: str) -> None:
        """Delete a template."""
        self._repository.delete(template_id)

    def generate_from_template(self, template_id: str) -> GenerateResponse:
        """Create a dataset from a stored template."""
        template = self.get_template(template_id)
        request = GenerateRequest(
            industry=template.industry,
            scenario=template.scenario,
            customers=template.customers,
            products=template.products,
            stores=template.stores,
            orders=template.orders,
            export=ExportFormat(template.export_type),
            quality=self._build_quality_config(template.quality),
        )
        generated = self._generation_service.generate(request)
        zip_path = Path(generated.export.zip_path)
        return GenerateResponse(
            download_url=str(zip_path.name),
            generated_files=[Path(path).name for path in generated.export.files],
            row_counts={name: len(table) for name, table in generated.tables.items()},
            generated_at=generated.export.generated_at,
            scenario=generated.scenario,
            quality=generated.quality,
            challenge_title=generated.challenge.title,
            difficulty=generated.challenge.difficulty,
            estimated_time=generated.challenge.estimated_completion_time,
            challenge_pdf_url="",
        )

    def _validate_name_is_unique(self, name: str) -> None:
        for template in self._repository.list():
            if template.name.lower() == name.lower():
                raise ValueError(f"template name already exists: {name}")

    def _validate_payload(
        self, payload: TemplateCreate | TemplateModel | TemplateUpdate
    ) -> None:
        from app.plugins.registry import create_default_plugin_registry

        plugin_registry = create_default_plugin_registry()
        try:
            plugin_registry.get(payload.industry)
        except ValueError as error:
            raise ValueError("industry must be a supported industry") from error
        if payload.scenario and payload.scenario not in {
            "none",
            "black_friday",
            "christmas",
            "summer_sale",
            "recession",
        }:
            raise ValueError("unsupported scenario")
        if payload.quality:
            for value in payload.quality.values():
                if value < 0 or value > 100:
                    raise ValueError("quality values must be between 0 and 100")
        if any(
            getattr(payload, field, None) is None
            for field in ["customers", "products", "stores", "orders"]
        ):
            return
        if (
            payload.customers <= 0
            or payload.products <= 0
            or payload.stores <= 0
            or payload.orders <= 0
        ):
            raise ValueError("counts must be greater than zero")

    def _build_quality_config(self, quality: Mapping[str, float]):
        from app.models.generation import QualityConfig

        return QualityConfig(**quality)
