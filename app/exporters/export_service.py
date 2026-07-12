"""Application service for complete dataset exports."""

from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
from typing import Callable, Mapping
from time import perf_counter

import pandas as pd

from app.challenges.base import ChallengePack
from app.challenges.writer import ChallengePackWriter
from app.config import EXPORTS_DIR
from app.core.metrics import metrics
from app.exporters.csv_exporter import CSVExporter
from app.exporters.data_dictionary import DataDictionaryGenerator
from app.exporters.excel_exporter import ExcelExporter
from app.exporters.readme_generator import ReadmeGenerator
from app.exporters.storage import ExportStorageLimitError, ExportStorageManager
from app.exporters.zip_exporter import ZipExporter


logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ExportResult:
    """Locations of a completed dataset export."""

    folder_path: str
    zip_path: str
    files: list[str]
    generated_at: datetime
    duration_ms: float = 0.0


class ExportService:
    """Coordinate interchangeable exporters into a complete dataset bundle."""

    def __init__(
        self,
        exports_root: Path | None = None,
        csv_exporter: CSVExporter | None = None,
        excel_exporter: ExcelExporter | None = None,
        zip_exporter: ZipExporter | None = None,
        dictionary_generator: DataDictionaryGenerator | None = None,
        readme_generator: ReadmeGenerator | None = None,
        challenge_writer: ChallengePackWriter | None = None,
        clock: Callable[[], datetime] | None = None,
        storage_manager: ExportStorageManager | None = None,
    ) -> None:
        self._exports_root = exports_root or EXPORTS_DIR
        self._csv_exporter = csv_exporter or CSVExporter()
        self._excel_exporter = excel_exporter or ExcelExporter()
        self._zip_exporter = zip_exporter or ZipExporter()
        self._dictionary_generator = dictionary_generator or DataDictionaryGenerator()
        self._readme_generator = readme_generator or ReadmeGenerator()
        self._challenge_writer = challenge_writer or ChallengePackWriter()
        self._clock = clock or datetime.now
        from app.core.settings import get_settings

        current_settings = get_settings()
        self._storage_manager = storage_manager or ExportStorageManager(
            self._exports_root,
            current_settings.export_ttl_hours,
            current_settings.max_export_storage_mb,
        )

    def export(
        self,
        tables: Mapping[str, pd.DataFrame],
        dataset_name: str = "Retail",
        quality_summary: Mapping[str, float] | None = None,
        challenge_pack: ChallengePack | None = None,
    ) -> ExportResult:
        """Write CSVs and documentation, then return a ZIP bundle result."""
        normalized_tables = self._validate_tables(tables)
        maintenance = self._storage_manager.maintain()
        started = perf_counter()
        generated_at = self._clock()
        export_name = f"{dataset_name}_{generated_at.strftime('%Y%m%d_%H%M%S')}"
        folder_path = self._exports_root / export_name
        if folder_path.exists():
            export_name = f"{export_name}_{generated_at.strftime('%f')}"
            folder_path = self._exports_root / export_name
        folder_path.mkdir(parents=True, exist_ok=False)

        zip_path = self._exports_root / f"{export_name}.zip"
        try:
            csv_paths = self._csv_exporter.export(normalized_tables, folder_path)
            dictionary = self._dictionary_generator.generate(normalized_tables)
            dictionary_path = self._excel_exporter.export(
                dictionary, folder_path / "data_dictionary.xlsx", "Data Dictionary"
            )
            readme_path = folder_path / "README.md"
            readme_path.write_text(
                self._readme_generator.generate(
                    dataset_name,
                    generated_at,
                    normalized_tables,
                    quality_summary,
                    challenge_pack.title if challenge_pack else None,
                ),
                encoding="utf-8",
            )
            challenge_paths = (
                self._challenge_writer.write(challenge_pack, folder_path)
                if challenge_pack
                else []
            )
            zip_path = self._zip_exporter.export(folder_path, zip_path)
            maintenance = self._storage_manager.maintain({folder_path, zip_path})
        except ExportStorageLimitError:
            self._storage_manager.remove_paths({folder_path, zip_path})
            raise
        except Exception:
            self._storage_manager.remove_paths({folder_path, zip_path})
            raise
        files = [*csv_paths, dictionary_path, readme_path, *challenge_paths]

        metrics.record_storage_maintenance(
            maintenance.expired_entries_removed,
            maintenance.capacity_entries_removed,
            maintenance.usage_bytes,
        )

        duration_ms = (perf_counter() - started) * 1000
        logger.info(
            "dataset_exported",
            extra={
                "dataset_name": dataset_name,
                "table_count": len(normalized_tables),
                "file_count": len(files),
                "duration_ms": round(duration_ms, 2),
                "storage_bytes": maintenance.usage_bytes,
                "cleanup_count": (
                    maintenance.expired_entries_removed
                    + maintenance.capacity_entries_removed
                ),
            },
        )
        return ExportResult(
            folder_path=str(folder_path),
            zip_path=str(zip_path),
            files=[str(path) for path in files],
            generated_at=generated_at,
            duration_ms=duration_ms,
        )

    @staticmethod
    def _validate_tables(tables: Mapping[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        if not tables:
            raise ValueError("at least one table is required for export")
        normalized_tables = dict(tables)
        for table_name, dataframe in normalized_tables.items():
            if not table_name or not table_name.replace("_", "").isalnum():
                raise ValueError(
                    "table names must contain only letters, numbers, and underscores"
                )
            if not isinstance(dataframe, pd.DataFrame):
                raise TypeError(f"{table_name} must be a pandas DataFrame")
        return normalized_tables
