"""Retail data quality rules."""

from app.data_quality.registry import QualityRegistry
from app.data_quality.retail.duplicates import DuplicatesRule
from app.data_quality.retail.invalid_formats import InvalidFormatsRule
from app.data_quality.retail.missing_values import MissingValuesRule
from app.data_quality.retail.outliers import OutliersRule
from app.data_quality.retail.referential_noise import ReferentialNoiseRule


def create_retail_quality_registry() -> QualityRegistry:
    """Create the default registry of retail quality rules."""
    return QualityRegistry(
        [
            MissingValuesRule(),
            DuplicatesRule(),
            OutliersRule(),
            InvalidFormatsRule(),
            ReferentialNoiseRule(),
        ]
    )


__all__ = ["create_retail_quality_registry"]
