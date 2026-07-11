from __future__ import annotations

from app.challenges.base import ChallengePack
from app.data_quality import QualityEngine
from app.exporters import ExportService
from app.plugins.base import BaseIndustryPlugin
from app.plugins.banking.generator import (
    BankingDatasetGenerator,
    BankingGenerationConfig,
)
from app.plugins.banking.metadata import BankingPluginMetadata
from app.plugins.banking.quality import create_banking_quality_registry
from app.plugins.banking.scenarios import (
    FraudSpikeScenario,
    HolidaySpendingScenario,
    InterestRateHikeScenario,
    LoanDefaultWaveScenario,
    NoneScenario,
)
from app.plugins.banking.templates import BankingTemplates
from app.plugins.interfaces import PluginGenerationConfig, PluginGenerationResult
from app.scenarios.registry import ScenarioRegistry


class BankingPlugin(BaseIndustryPlugin):
    def __init__(self) -> None:
        self._metadata = BankingPluginMetadata()

    @property
    def id(self) -> str:
        return "banking"

    def name(self) -> str:
        return self._metadata.industry

    def description(self) -> str:
        return self._metadata.description

    def version(self) -> str:
        return self._metadata.version

    def supported_scenarios(self) -> list[str]:
        return [
            "none",
            "fraud_spike",
            "interest_rate_hike",
            "loan_default_wave",
            "holiday_spending",
        ]

    def supported_quality_rules(self) -> list[str]:
        return [
            "missing_values",
            "duplicates",
            "outliers",
            "invalid_formats",
            "referential_noise",
        ]

    def default_templates(self) -> list[dict[str, object]]:
        return BankingTemplates.default_templates()

    def default_counts(self) -> dict[str, int]:
        return {
            "customers": 10_000,
            "branches": 20,
            "accounts": 15_000,
            "transactions": 100_000,
            "loans": 5_000,
            "credit_cards": 4_000,
            "payments": 20_000,
        }

    def frontend_metadata(self) -> dict[str, object]:
        """Expose the Banking plugin's complete dynamic frontend contract."""
        fields = [
            _number_field("customers", "Customers", 10_000),
            _number_field("accounts", "Accounts", 15_000),
            _number_field("transactions", "Transactions", 100_000),
            _number_field("loans", "Loans", 5_000),
            _number_field("branches", "Branches", 20),
            _number_field("credit_cards", "Credit Cards", 4_000),
        ]
        return {
            **self.metadata(),
            "icon": "landmark",
            "color": "#0f766e",
            "configuration_fields": fields,
            "supported_scenarios": self.supported_scenarios(),
            "supported_templates": self.default_templates(),
            "kpis": ["Total Deposits", "Total Loans", "Default Rate", "Fraud Rate"],
            "dashboard_suggestions": ["Branch profitability", "Portfolio risk", "Customer product penetration"],
            "challenge_types": ["Credit Portfolio Review", "Fraud Investigation"],
            "field_layout": [{"title": "Dataset Size", "fields": [field["key"] for field in fields], "columns": 2}],
            "generation_available": True,
        }

    def generate(
        self,
        config: PluginGenerationConfig,
        export_service: ExportService | None = None,
    ) -> PluginGenerationResult:
        self.validate(config)
        customers = config.get_count("customers")
        transactions = config.get_count("transactions", config.get_count("orders"))
        generation_config = BankingGenerationConfig(
            customers=customers,
            branches=config.get_count("branches", config.get_count("stores")),
            accounts=config.get_count("accounts", max(1, customers // 2)),
            transactions=transactions,
            loans=config.get_count("loans", max(1, customers // 10)),
            credit_cards=config.get_count("credit_cards", max(1, customers // 20)),
            payments=max(1, transactions // 2),
            seed=42,
        )
        tables = BankingDatasetGenerator(generation_config).generate()
        scenario_registry = ScenarioRegistry(
            [
                NoneScenario(),
                FraudSpikeScenario(),
                InterestRateHikeScenario(),
                LoanDefaultWaveScenario(),
                HolidaySpendingScenario(),
            ]
        )
        scenario = scenario_registry.get(config.scenario)
        tables = scenario.apply(tables)
        quality_engine = QualityEngine(create_banking_quality_registry())
        quality = dict(config.quality)
        tables = quality_engine.apply(tables, quality)
        challenge = self._build_challenge(tables, scenario.name, quality)
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
            raise ValueError("Invalid industry for banking plugin")
        if config.scenario not in self.supported_scenarios():
            raise ValueError("Unsupported scenario")
        for rule_name in config.quality:
            if rule_name not in self.supported_quality_rules():
                raise ValueError("Unsupported quality rule")

    def metadata(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name(),
            "description": self.description(),
            "version": self.version(),
            "status": "available",
        }

    def _build_challenge(
        self, tables: dict[str, object], scenario: str, quality: dict[str, float]
    ) -> ChallengePack:
        metadata = {
            "industry": self.id,
            "row_counts": {name: len(table) for name, table in tables.items()},
            "dataset_size": sum(len(table) for table in tables.values()),
        }
        quality_issues = [name for name, value in quality.items() if value > 0]
        quality_context = (
            f"The source also contains intentional {', '.join(quality_issues).replace('_', ' ')} issues."
            if quality_issues
            else "The source is clean."
        )
        challenge_titles = {
            "fraud_spike": "Fraud Investigation",
            "interest_rate_hike": "Credit Risk Analysis",
            "loan_default_wave": "Loan Portfolio Analysis",
            "holiday_spending": "Customer Segmentation",
        }
        title = challenge_titles.get(scenario, "Executive Banking Dashboard")
        return ChallengePack(
            title=title,
            business_story=f"A banking team needs an executive-ready view of deposits, credit risk, fraud indicators, and branch performance. {quality_context}",
            business_problem="Analyze customer, account, transaction, loan, and card performance to support decisions on risk and growth.",
            difficulty="Intermediate",
            recommended_tools=["SQL", "Power BI", "Python", "Tableau"],
            dashboard_requirements=[
                "KPI summary",
                "Fraud monitoring",
                "Loan portfolio review",
            ],
            sql_questions=[
                "Which branches have the highest average balances?",
                "What is the default rate by customer segment?",
            ],
            excel_questions=["Summarize balances by account type."],
            python_questions=["Build a customer segmentation model."],
            powerbi_tasks=["Create a banking dashboard."],
            tableau_tasks=["Create a risk dashboard."],
            kpis=[
                "Total Deposits",
                "Total Loans",
                "Average Balance",
                "Loan Default Rate",
                "Credit Utilization",
                "Fraud Rate",
                "Customer Growth",
                "Branch Performance",
            ],
            deliverables=["Executive Dashboard", "SQL Script", "Python Notebook"],
            success_criteria=[
                "Clear executive narrative",
                "Validated KPIs",
                "Risk-based recommendations",
            ],
            estimated_completion_time="6–8 hours",
            machine_learning_ideas=["Fraud detection", "Credit risk segmentation"],
            dataset_metadata=metadata,
            scenario=scenario,
            quality=quality,
        )


def _number_field(key: str, label: str, default: int) -> dict[str, object]:
    return {
        "key": key,
        "label": label,
        "type": "number",
        "default": default,
        "minimum": 1,
        "maximum": 1_000_000,
    }
