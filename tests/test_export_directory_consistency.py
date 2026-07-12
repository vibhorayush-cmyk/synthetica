"""Regression tests for configured export-directory behavior."""

from pathlib import Path

from app.config import EXPORTS_DIR
from app.exporters import ExportService


def test_default_export_service_uses_download_export_root() -> None:
    """Generated archives default to the same root served by download routes."""
    service = ExportService()

    assert service._exports_root == EXPORTS_DIR
    assert service._exports_root == Path(EXPORTS_DIR)
