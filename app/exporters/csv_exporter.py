"""CSV export implementation."""

from pathlib import Path

import pandas as pd


class CSVExporter:
    """Write one DataFrame per CSV file."""

    def export(self, tables: dict[str, pd.DataFrame], destination: Path) -> list[Path]:
        """Write tables to ``destination`` and return their file paths."""
        destination.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        for table_name, dataframe in tables.items():
            path = destination / f"{table_name}.csv"
            dataframe.to_csv(path, index=False)
            paths.append(path)
        return paths
