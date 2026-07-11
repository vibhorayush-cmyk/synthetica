from __future__ import annotations

from app.challenges.registry import ChallengeRegistry
from app.challenges.retail import create_retail_challenge_registry
from app.data_quality import QualityEngine
from app.data_quality.retail import create_retail_quality_registry
from app.exporters import ExportService
from app.generators.retail import RetailDatasetGenerator, RetailGenerationConfig
from app.plugins.base import BaseIndustryPlugin
from app.plugins.interfaces import PluginGenerationConfig, PluginGenerationResult
from app.scenarios.registry import ScenarioRegistry
from app.scenarios.retail import create_retail_scenario_registry


class RetailPlugin(BaseIndustryPlugin):
    @property
    def id(self) -> str:
        return "retail"

    def name(self) -> str:
        return "Retail"

    def description(self) -> str:
        return "Synthetic retail dataset generation for sales, inventory, and customer analytics."

    def version(self) -> str:
        return "1.0"

    def supported_scenarios(self) -> list[str]:
        return ["none", "black_friday", "christmas", "summer_sale", "recession"]

    def supported_quality_rules(self) -> list[str]:
        return [
            "missing_values",
            "duplicates",
            "outliers",
            "invalid_formats",
            "referential_noise",
        ]

    def default_templates(self) -> list[dict[str, object]]:
        return [{"name": "Retail Starter", "industry": "retail"}]

    def default_counts(self) -> dict[str, int]:
        return {"customers": 10_000, "products": 500, "stores": 50, "orders": 100_000}

    def frontend_metadata(self) -> dict[str, object]:
        """Expose the Retail plugin's complete dynamic frontend contract."""
        fields = [
            _number_field("customers", "Customers", 10_000),
            _number_field("products", "Products", 500),
            _number_field("stores", "Stores", 50),
            _number_field("orders", "Orders", 100_000),
        ]
        return {
            **self.metadata(),
            "icon": "shopping-bag",
            "color": "#4f46e5",
            "configuration_fields": fields,
            "supported_scenarios": self.supported_scenarios(),
            "supported_templates": self.default_templates(),
            "kpis": ["Total Revenue", "Profit Margin", "Average Order Value", "Return Rate"],
            "dashboard_suggestions": [
                "Executive performance dashboard",
                "Category and customer drillthrough",
                "Geographic sales analysis",
            ],
            "challenge_types": ["Retail Performance Investigation", "Promotional Margin Review"],
            "field_layout": [{"title": "Dataset Size", "fields": [field["key"] for field in fields], "columns": 2}],
            "generation_available": True,
        }

    def generate(
        self,
        config: PluginGenerationConfig,
        export_service: ExportService | None = None,
    ) -> PluginGenerationResult:
        self.validate(config)
        generation_config = RetailGenerationConfig(
            customers=config.get_count("customers"),
            products=config.get_count("products"),
            stores=config.get_count("stores"),
            orders=config.get_count("orders"),
            order_items=config.get_count("orders"),
        )
        tables = RetailDatasetGenerator(generation_config).generate()
        scenario_registry: ScenarioRegistry = create_retail_scenario_registry()
        scenario = scenario_registry.get(config.scenario)
        tables = scenario.apply(tables)
        quality_engine = QualityEngine(create_retail_quality_registry())
        quality = dict(config.quality)
        tables = quality_engine.apply(tables, quality)
        challenge_registry: ChallengeRegistry = create_retail_challenge_registry()
        challenge = challenge_registry.get("retail").generate(
            {
                "industry": "retail",
                "row_counts": {name: len(table) for name, table in tables.items()},
                "dataset_size": sum(len(table) for table in tables.values()),
            },
            scenario.name,
            quality,
        )
        exporter = export_service or ExportService()
        export = exporter.export(
            tables,
            dataset_name=self.name(),
            quality_summary=quality,
            challenge_pack=challenge,
        )
        return PluginGenerationResult(
            tables=tables,
            export=export,
            scenario=scenario.name,
            quality=quality,
            challenge=challenge,
        )

    def validate(self, config: PluginGenerationConfig) -> None:
        if config.industry != self.id:
            raise ValueError("Invalid industry for retail plugin")
        if config.scenario not in self.supported_scenarios():
            raise ValueError("Unsupported scenario")
        for rule_name in config.quality:
            if rule_name not in self.supported_quality_rules():
                raise ValueError("Unsupported quality rule")


def _number_field(key: str, label: str, default: int) -> dict[str, object]:
    return {
        "key": key,
        "label": label,
        "type": "number",
        "default": default,
        "minimum": 1,
        "maximum": 1_000_000,
    }
