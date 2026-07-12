"""Async service for user-owned reusable generation templates."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Template
from app.db.repositories import TemplateRepository
from app.models.generation import GenerateRequest, QualityConfig
from app.services.generation_service import GenerationService, get_generation_service
from app.templates.schemas import TemplateCreate, TemplateResponse, TemplateUpdate


class AsyncTemplateService:
    """Keep template CRUD isolated from persistence and generation adapters."""

    def __init__(
        self, session: AsyncSession, generation_service: GenerationService | None = None
    ) -> None:
        self._repository = TemplateRepository(session)
        self._generation_service = generation_service or get_generation_service()

    async def list(self, user_id: UUID) -> list[TemplateResponse]:
        return [self._to_response(item) for item in await self._repository.list_for_user(user_id)]

    async def get(self, template_id: UUID, user_id: UUID) -> TemplateResponse:
        template = await self._get_record(template_id, user_id)
        return self._to_response(template)

    async def create(self, user_id: UUID, payload: TemplateCreate) -> TemplateResponse:
        self._validate_payload(payload)
        if await self._repository.get_by_name(user_id, payload.name):
            raise ValueError("template name already exists")
        template = Template(
            user_id=user_id,
            name=payload.name,
            description=payload.description,
            industry=payload.industry,
            scenario=payload.scenario,
            configuration=self._configuration(payload),
            export_type=payload.export_type,
            quality=payload.quality,
            difficulty=payload.difficulty,
        )
        return self._to_response(await self._repository.create(template))

    async def update(
        self, template_id: UUID, user_id: UUID, payload: TemplateUpdate
    ) -> TemplateResponse:
        template = await self._get_record(template_id, user_id)
        changes = payload.model_dump(exclude_unset=True)
        if "name" in changes and changes["name"] != template.name:
            if await self._repository.get_by_name(user_id, changes["name"]):
                raise ValueError("template name already exists")
        merged = self._to_response(template).model_copy(update=changes)
        self._validate_payload(merged)
        for field in ("name", "description", "industry", "scenario", "export_type", "quality", "difficulty"):
            if field in changes:
                setattr(template, field, changes[field])
        if any(field in changes for field in ("customers", "products", "stores", "orders")):
            template.configuration = self._configuration(merged)
        template.version += 1
        return self._to_response(await self._repository.save(template))

    async def delete(self, template_id: UUID, user_id: UUID) -> None:
        await self._repository.delete(await self._get_record(template_id, user_id))

    async def generate_request(self, template_id: UUID, user_id: UUID) -> GenerateRequest:
        template = await self._get_record(template_id, user_id)
        return GenerateRequest(
            industry=template.industry,
            scenario=template.scenario,
            configuration=template.configuration,
            export=template.export_type,
            quality=QualityConfig(**template.quality),
        )

    async def _get_record(self, template_id: UUID, user_id: UUID) -> Template:
        template = await self._repository.get_for_user(template_id, user_id)
        if not template:
            raise ValueError("template not found")
        return template

    @staticmethod
    def _configuration(payload: TemplateCreate | TemplateResponse) -> dict[str, int]:
        return {
            "customers": payload.customers,
            "products": payload.products,
            "stores": payload.stores,
            "orders": payload.orders,
        }

    @staticmethod
    def _validate_payload(payload: TemplateCreate | TemplateResponse) -> None:
        from app.plugins.registry import create_default_plugin_registry

        try:
            create_default_plugin_registry().get(payload.industry)
        except ValueError as error:
            raise ValueError("industry must be a supported industry") from error
        if any(value < 0 or value > 100 for value in payload.quality.values()):
            raise ValueError("quality values must be between 0 and 100")

    @staticmethod
    def _to_response(template: Template) -> TemplateResponse:
        return TemplateResponse(
            id=str(template.id),
            name=template.name,
            description=template.description,
            industry=template.industry,
            scenario=template.scenario,
            customers=template.configuration.get("customers", 1),
            products=template.configuration.get("products", 1),
            stores=template.configuration.get("stores", 1),
            orders=template.configuration.get("orders", 1),
            export_type=template.export_type,
            quality=template.quality,
            difficulty=template.difficulty,
            created_at=template.created_at,
            updated_at=template.updated_at,
            version=template.version,
        )
