"""Reusable retail inventory and visualization challenge sections."""


class InventoryAnalysisChallenge:
    """Provide dashboard and spreadsheet deliverables."""

    @staticmethod
    def dashboard_requirements() -> list[str]:
        return [
            "Executive KPI cards for revenue, profit, margin, and return rate.",
            "Sales and profit trends with scenario-aware annotations.",
            "Category, product, customer, and geographic performance views.",
            "A data quality view that quantifies missing values, duplicates, and outliers.",
        ]

    @staticmethod
    def powerbi_tasks() -> list[str]:
        return [
            "Build an Executive Dashboard with KPI Cards.",
            "Create Sales Trend, Profit Trend, Category Performance, and Customer Segmentation views.",
            "Add Geographic Sales, a drillthrough page, bookmarks, and report tooltips.",
        ]

    @staticmethod
    def tableau_tasks() -> list[str]:
        return [
            "Build an executive sales and margin dashboard.",
            "Create interactive category and store filters with customer drilldowns.",
            "Document calculations and data-quality assumptions in a dashboard tooltip.",
        ]

    @staticmethod
    def excel_questions() -> list[str]:
        return [
            "Build Pivot Tables and Pivot Charts for category performance.",
            "Use Conditional Formatting to flag margin and return-rate risk.",
            "Use XLOOKUP to enrich order items and Power Query to clean source data.",
        ]
