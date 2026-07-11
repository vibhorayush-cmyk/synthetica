from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from app.challenges.retail.executive_dashboard import (
    ExecutiveDashboardChallengeGenerator,
)
from app.exporters.export_service import ExportService


def test_retail_challenge_generator_adapts_to_scenario_and_quality() -> None:
    generator = ExecutiveDashboardChallengeGenerator()
    pack = generator.generate(
        dataset_metadata={
            "industry": "retail",
            "row_counts": {"customers": 10_000, "orders": 20_000},
            "dataset_size": 30_000,
        },
        scenario="black_friday",
        quality={"missing_values": 12.5, "duplicates": 3.0},
    )

    assert pack.title == "Retail Performance Investigation"
    assert "Black Friday" in pack.business_story
    assert pack.difficulty == "Advanced"
    assert "SQL" in pack.recommended_tools
    assert "Top Customers" in pack.kpis
    assert pack.estimated_completion_time == "10–14 hours"


def test_export_service_includes_challenge_pack_artifacts() -> None:
    generator = ExecutiveDashboardChallengeGenerator()
    pack = generator.generate(
        dataset_metadata={"row_counts": {"orders": 100}, "dataset_size": 100},
        scenario="none",
        quality={},
    )

    with TemporaryDirectory() as temp_dir:
        export_service = ExportService(exports_root=Path(temp_dir))
        result = export_service.export(
            {"orders": pd.DataFrame({"order_id": [1, 2]})},
            dataset_name="Retail",
            challenge_pack=pack,
        )

        folder = Path(result.folder_path)
        assert (folder / "challenge.md").is_file()
        assert (folder / "challenge.pdf").is_file()
        assert (folder / "requirements.md").is_file()
        assert (folder / "dataset_overview.md").is_file()
        assert Path(result.zip_path).is_file()
