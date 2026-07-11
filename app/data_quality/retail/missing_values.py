"""Missing-value injection for retail datasets."""

import numpy as np
import pandas as pd

from app.data_quality.base import BaseQualityRule
from app.data_quality.retail.helpers import RetailQualityHelper


class MissingValuesRule(BaseQualityRule):
    """Set selected non-key retail attributes to null values."""

    name = "missing_values"
    target_columns = {
        "customers": ("Email", "Phone", "Age", "City"),
        "stores": ("StoreName", "City"),
        "order_items": ("Discount",),
    }

    def apply(
        self,
        dataset: dict[str, pd.DataFrame],
        percentage: float = 0,
        random: np.random.Generator | None = None,
    ) -> dict[str, pd.DataFrame]:
        """Inject nulls into available configured columns, never into IDs."""
        random = self.random_or_default(random)
        for table_name, columns in self.target_columns.items():
            dataframe = dataset.get(table_name)
            if dataframe is None:
                continue
            for column_name in columns:
                if column_name in dataframe:
                    indexes = RetailQualityHelper.random_indexes(
                        dataframe, percentage, random
                    )
                    dataframe.loc[indexes, column_name] = None
        return dataset
