"""ZIP archive export implementation."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


class ZipExporter:
    """Compress a dataset folder into a ZIP archive."""

    def export(self, source_folder: Path, destination: Path) -> Path:
        """Archive every file in ``source_folder`` under its folder name."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        with ZipFile(destination, mode="w", compression=ZIP_DEFLATED) as archive:
            for file_path in sorted(source_folder.rglob("*")):
                if file_path.is_file():
                    archive.write(
                        file_path, file_path.relative_to(source_folder.parent)
                    )
        return destination
