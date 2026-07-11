from __future__ import annotations


class BankingTemplates:
    """Default templates exposed by the banking plugin."""

    @staticmethod
    def default_templates() -> list[dict[str, object]]:
        return [
            {"name": "Banking Beginner", "industry": "banking"},
            {"name": "Banking Power BI", "industry": "banking"},
            {"name": "Banking SQL", "industry": "banking"},
            {"name": "Banking Fraud Detection", "industry": "banking"},
            {"name": "Banking Machine Learning", "industry": "banking"},
        ]
