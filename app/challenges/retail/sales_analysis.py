"""Reusable retail sales-analysis challenge sections."""


class SalesAnalysisChallenge:
    """Provide sales investigation questions and KPIs."""

    def sql_questions(self, advanced: bool) -> list[str]:
        questions = [
            "Find the top 10 products by revenue.",
            "Calculate month-over-month sales growth.",
            "Find products with high discounts but low profit.",
            "Compare revenue, profit, and discount rate by category.",
        ]
        if advanced:
            questions.append(
                "Create a rolling 30-day revenue and margin trend using window functions."
            )
        return questions

    @staticmethod
    def kpis() -> list[str]:
        return [
            "Total Revenue",
            "Total Profit",
            "Profit Margin",
            "Average Order Value",
            "Top Categories",
            "Discount %",
            "Inventory Turnover",
        ]
