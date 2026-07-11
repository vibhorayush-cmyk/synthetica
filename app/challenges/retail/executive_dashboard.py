"""Retail executive dashboard learning pack generator."""

from collections.abc import Mapping

from app.challenges.base import BaseChallengeGenerator, ChallengePack
from app.challenges.retail.customer_analysis import CustomerAnalysisChallenge
from app.challenges.retail.inventory_analysis import InventoryAnalysisChallenge
from app.challenges.retail.sales_analysis import SalesAnalysisChallenge


_SCENARIO_STORIES = {
    "black_friday": "Synthetic Retail Inc. experienced record revenue during Black Friday. Despite higher sales, profit margins declined and the executive team needs an investigation.",
    "christmas": "Synthetic Retail Inc. saw a seasonal Christmas surge in gifts, toys, fashion, and returns. Leaders need to separate healthy demand from post-holiday margin pressure.",
    "summer_sale": "Synthetic Retail Inc. launched a summer sale that lifted seasonal demand while increasing promotional discount exposure.",
    "recession": "Synthetic Retail Inc. is operating through a recession. Customers are shifting toward lower-cost products and average order value is under pressure.",
    "none": "Synthetic Retail Inc. wants an executive-ready view of baseline retail performance, customer behavior, and operational risk.",
}


class ExecutiveDashboardChallengeGenerator(BaseChallengeGenerator):
    """Compose a professional retail portfolio case study from reusable sections."""

    industry = "retail"

    def __init__(self) -> None:
        self._sales = SalesAnalysisChallenge()
        self._customers = CustomerAnalysisChallenge()
        self._inventory = InventoryAnalysisChallenge()

    def generate(
        self,
        dataset_metadata: Mapping[str, object],
        scenario: str,
        quality: Mapping[str, float],
    ) -> ChallengePack:
        """Generate a scenario- and scale-aware retail investigation brief."""
        difficulty, estimated_time = self._complexity(dataset_metadata, quality)
        advanced = difficulty == "Advanced"
        quality_issues = [name for name, value in quality.items() if value > 0]
        quality_context = (
            f"The source also contains intentional {', '.join(quality_issues).replace('_', ' ')} issues, so the team must validate metrics before presenting conclusions."
            if quality_issues
            else "The source is clean, allowing the team to focus on business interpretation and dashboard design."
        )
        return ChallengePack(
            title="Retail Performance Investigation",
            business_story=f"{_SCENARIO_STORIES.get(scenario, _SCENARIO_STORIES['none'])} {quality_context}",
            business_problem="Diagnose revenue, profit, customer, and operational performance; then recommend the most valuable actions for the executive team.",
            difficulty=difficulty,
            recommended_tools=["SQL", "Excel", "Python", "Power BI", "Tableau"],
            dashboard_requirements=self._inventory.dashboard_requirements(),
            sql_questions=self._sales.sql_questions(advanced)
            + self._customers.sql_questions(),
            excel_questions=self._inventory.excel_questions(),
            python_questions=self._customers.python_questions(),
            powerbi_tasks=self._inventory.powerbi_tasks(),
            tableau_tasks=self._inventory.tableau_tasks(),
            kpis=self._sales.kpis() + ["Top Customers", "Return Rate"],
            deliverables=[
                "Executive Dashboard",
                "Power BI File",
                "SQL Script",
                "Python Notebook",
                "Presentation Slides",
            ],
            success_criteria=self._success_criteria(advanced),
            estimated_completion_time=estimated_time,
            machine_learning_ideas=self._customers.machine_learning_ideas(),
            dataset_metadata=dataset_metadata,
            scenario=scenario,
            quality=quality,
        )

    @staticmethod
    def _complexity(
        metadata: Mapping[str, object], quality: Mapping[str, float]
    ) -> tuple[str, str]:
        row_counts = metadata.get("row_counts", {})
        total_rows = sum(row_counts.values()) if isinstance(row_counts, dict) else 0
        has_quality_issues = any(value > 0 for value in quality.values())
        if total_rows >= 100_000 or (total_rows >= 25_000 and has_quality_issues):
            return "Advanced", "10–14 hours"
        if total_rows >= 10_000 or has_quality_issues or total_rows >= 5_000:
            return "Intermediate", "6–8 hours"
        return "Foundational", "3–4 hours"

    @staticmethod
    def _success_criteria(advanced: bool) -> list[str]:
        criteria = [
            "Reproducible calculations with documented definitions.",
            "A concise executive narrative that distinguishes insight from observation.",
            "Validated handling of data quality issues before KPI publication.",
        ]
        if advanced:
            criteria.append(
                "A scalable semantic model and performance-conscious analytical approach."
            )
        return criteria
