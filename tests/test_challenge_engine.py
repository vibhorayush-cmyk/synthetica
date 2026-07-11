"""Tests for retail learning-pack generation and export."""

from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from app.challenges.retail.executive_dashboard import (
    ExecutiveDashboardChallengeGenerator,
)
from app.exporters import ExportService


def test_challenge_generation_changes_story_and_complexity() -> None:
    """Scenario wording and difficulty respond to metadata and quality settings."""
    generator = ExecutiveDashboardChallengeGenerator()
    foundational = generator.generate(
        {"row_counts": {"orders": 100}}, "none", {"missing_values": 0}
    )
    black_friday = generator.generate(
        {"row_counts": {"orders": 100_000}},
        "black_friday",
        {"missing_values": 5},
    )

    assert foundational.difficulty == "Foundational"
    assert black_friday.difficulty == "Advanced"
    assert "Black Friday" in black_friday.business_story
    assert black_friday.estimated_completion_time == "10–14 hours"
    assert "Find the top 10 products by revenue." in black_friday.sql_questions


def test_challenge_files_are_written_into_export_and_zip(tmp_path: Path) -> None:
    """Challenge Markdown, PDF, requirements, and overview ship in the ZIP bundle."""
    pack = ExecutiveDashboardChallengeGenerator().generate(
        {"row_counts": {"customers": 1, "orders": 1}},
        "none",
        {"missing_values": 0},
    )
    result = ExportService(
        exports_root=tmp_path,
        clock=lambda: datetime(2026, 7, 12, 15, 0, 0),
    ).export(
        {"customers": pd.DataFrame({"CustomerID": [100_000]})},
        challenge_pack=pack,
    )
    folder = Path(result.folder_path)
    readme = (folder / "README.md").read_text(encoding="utf-8")

    assert {
        "challenge.md",
        "challenge.pdf",
        "requirements.md",
        "dataset_overview.md",
    }.issubset({path.name for path in folder.iterdir()})
    assert "Learning Pack" in readme
    assert pack.title in readme
    with ZipFile(result.zip_path) as archive:
        assert "Retail_20260712_150000/challenge.pdf" in archive.namelist()
