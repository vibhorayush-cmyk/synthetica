"""Excel export implementation."""

from pathlib import Path

import pandas as pd


class ExcelExporter:
    """Write DataFrames to Excel workbooks."""

    def export(
        self, dataframe: pd.DataFrame, destination: Path, sheet_name: str
    ) -> Path:
        """Write one DataFrame to a worksheet and return the workbook path."""
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            with pd.ExcelWriter(destination, engine="openpyxl") as writer:
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        except ModuleNotFoundError:
            with pd.ExcelWriter(destination, engine="xlsxwriter") as writer:
                dataframe.to_excel(writer, sheet_name=sheet_name, index=False)
        return destination
