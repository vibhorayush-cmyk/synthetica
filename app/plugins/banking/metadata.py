from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BankingPluginMetadata:
    industry: str = "Banking"
    description: str = (
        "Synthetic banking datasets for SQL, Power BI, Tableau, Python and Machine Learning practice."
    )
    version: str = "1.0"
