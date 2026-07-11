"""Bounded performance regression checks for the retail pipeline."""

from time import perf_counter

from app.generators.retail import RetailDatasetGenerator, RetailGenerationConfig


def test_small_dataset_generation_completes_within_regression_budget() -> None:
    """Guard against accidental quadratic behavior in baseline generation."""
    started = perf_counter()
    dataset = RetailDatasetGenerator(
        RetailGenerationConfig(
            customers=100,
            products=50,
            stores=5,
            orders=1_000,
            order_items=1_000,
            seed=1,
        )
    ).generate()

    assert sum(len(table) for table in dataset.values()) == 2_155
    assert perf_counter() - started < 5
