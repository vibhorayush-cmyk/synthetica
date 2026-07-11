"""Reusable retail customer-analysis challenge sections."""


class CustomerAnalysisChallenge:
    """Provide customer analysis and data-cleaning tasks."""

    @staticmethod
    def sql_questions() -> list[str]:
        return [
            "Find customers with the highest lifetime value.",
            "Detect duplicate customers.",
            "Identify missing emails and invalid contact formats.",
        ]

    @staticmethod
    def python_questions() -> list[str]:
        return [
            "Load the dataset and perform exploratory data analysis.",
            "Complete a missing-value and duplicate-record analysis.",
            "Detect outliers and explain their effect on KPI calculations.",
            "Build a correlation matrix and engineer customer-value features.",
            "Create a baseline sales-forecasting experiment.",
        ]

    @staticmethod
    def machine_learning_ideas() -> list[str]:
        return [
            "Customer Segmentation",
            "Sales Forecasting",
            "Return Prediction",
            "Fraud Detection",
            "Demand Forecasting",
        ]
