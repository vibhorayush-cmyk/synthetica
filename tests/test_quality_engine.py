"""Unit tests for the reusable retail data quality engine."""

from app.data_quality import QualityEngine
from app.data_quality.retail import create_retail_quality_registry
from app.generators.retail import RetailDatasetGenerator, RetailGenerationConfig


def test_missing_values_approximately_match_requested_percentage() -> None:
    """Missing-value injection affects configured non-key fields at the rate given."""
    dataset = _baseline_dataset()
    updated = _engine().apply(dataset, {"missing_values": 10})

    missing_email_rate = updated["customers"]["Email"].isna().mean() * 100
    missing_discount_rate = updated["order_items"]["Discount"].isna().mean() * 100

    assert 8 <= missing_email_rate <= 12
    assert 8 <= missing_discount_rate <= 12
    assert updated["customers"]["CustomerID"].notna().all()
    assert updated["products"]["ProductID"].notna().all()
    assert updated["stores"]["StoreID"].notna().all()
    assert updated["orders"]["OrderID"].notna().all()


def test_quality_rules_preserve_primary_keys_and_foreign_keys_by_default() -> None:
    """Non-noise rules introduce problems without breaking relational integrity."""
    dataset = _baseline_dataset()
    updated = _engine().apply(
        dataset,
        {
            "missing_values": 5,
            "duplicates": 5,
            "outliers": 5,
            "invalid_formats": 5,
        },
    )

    assert updated["customers"]["CustomerID"].is_unique
    assert updated["products"]["ProductID"].is_unique
    assert updated["stores"]["StoreID"].is_unique
    assert updated["orders"]["OrderID"].is_unique
    _assert_foreign_keys(updated)


def test_referential_noise_is_only_introduced_when_explicitly_enabled() -> None:
    """Referential noise creates invalid links only at a configured percentage."""
    dataset = _baseline_dataset()
    unchanged = _engine().apply(dataset, {"referential_noise": 0})
    noisy = _engine().apply(dataset, {"referential_noise": 10})

    assert _has_valid_foreign_keys(unchanged)
    assert not _has_valid_foreign_keys(noisy)


def _engine() -> QualityEngine:
    return QualityEngine(create_retail_quality_registry(), seed=7)


def _baseline_dataset():
    return RetailDatasetGenerator(
        RetailGenerationConfig(
            customers=100,
            products=50,
            stores=10,
            orders=100,
            order_items=100,
            seed=3,
        )
    ).generate()


def _assert_foreign_keys(dataset) -> None:
    assert _has_valid_foreign_keys(dataset)


def _has_valid_foreign_keys(dataset) -> bool:
    return (
        set(dataset["orders"]["CustomerID"]).issubset(
            set(dataset["customers"]["CustomerID"])
        )
        and set(dataset["orders"]["StoreID"]).issubset(
            set(dataset["stores"]["StoreID"])
        )
        and set(dataset["order_items"]["OrderID"]).issubset(
            set(dataset["orders"]["OrderID"])
        )
        and set(dataset["order_items"]["ProductID"]).issubset(
            set(dataset["products"]["ProductID"])
        )
    )
