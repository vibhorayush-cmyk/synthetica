"""Service boundary for dataset generation and export."""

from dataclasses import dataclass
import logging
from time import perf_counter
import tracemalloc

import pandas as pd

from app.challenges.base import ChallengePack
from app.core.metrics import metrics
from app.exporters import ExportResult, ExportService
from app.models.generation import GenerateRequest
from app.plugins.interfaces import PluginGenerationConfig
from app.plugins.registry import PluginRegistry, create_default_plugin_registry


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GeneratedDataset:
    """Generated tables and their complete export result."""

    tables: dict[str, pd.DataFrame]
    export: ExportResult
    scenario: str
    quality: dict[str, float]
    challenge: ChallengePack


class GenerationService:
    """Generate a dataset using the registered industry plugin."""

    def __init__(
        self,
        export_service: ExportService | None = None,
        plugin_registry: PluginRegistry | None = None,
    ) -> None:
        self._export_service = export_service or ExportService()
        self._plugin_registry = plugin_registry or create_default_plugin_registry()

    def generate(self, request: GenerateRequest) -> GeneratedDataset:
        """Generate tables and export their complete ZIP bundle."""
        total_started = perf_counter()
        tracemalloc.start()
        try:
            quality = request.quality.to_mapping()
            plugin = self._plugin_registry.get(request.industry)
            configuration = request.configuration or {
                key: value
                for key, value in {
                    "customers": request.customers,
                    "products": request.products,
                    "stores": request.stores,
                    "orders": request.orders,
                }.items()
                if value is not None
            }
            plugin_config = PluginGenerationConfig(
                industry=request.industry,
                scenario=request.scenario,
                customers=configuration.get("customers", 1),
                products=configuration.get("products", 1),
                stores=configuration.get("stores", 1),
                orders=configuration.get("orders", 1),
                export_type=request.export.value,
                quality=quality,
                configuration=configuration,
            )
            plugin.validate(plugin_config)
            result = plugin.generate(plugin_config, self._export_service)
            current, peak_memory = tracemalloc.get_traced_memory()
            del current
            total_ms = (perf_counter() - total_started) * 1000
            export_ms = getattr(result.export, "duration_ms", 0.0)
            metrics.record_success(total_ms - export_ms, export_ms, peak_memory)
            logger.info(
                "dataset_generated",
                extra={
                    "industry": request.industry,
                    "scenario": request.scenario,
                    "rows": sum(len(table) for table in result.tables.values()),
                    "duration_ms": round(total_ms, 2),
                    "peak_memory_bytes": peak_memory,
                },
            )
            return GeneratedDataset(
                tables=result.tables,
                export=result.export,
                scenario=result.scenario,
                quality=result.quality,
                challenge=result.challenge,
            )
        except Exception:
            metrics.record_failure()
            logger.exception(
                "dataset_generation_failed",
                extra={"industry": request.industry, "scenario": request.scenario},
            )
            raise
        finally:
            tracemalloc.stop()


def get_generation_service() -> GenerationService:
    """Provide the generation service for dependency injection."""
    return GenerationService()
