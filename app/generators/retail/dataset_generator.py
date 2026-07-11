"""Retail dataset orchestration."""

from dataclasses import dataclass

import pandas as pd

from app.generators.retail.context import GenerationContext
from app.generators.retail.customers import CustomersGenerator
from app.generators.retail.order_items import OrderItemsGenerator
from app.generators.retail.orders import OrdersGenerator
from app.generators.retail.products import ProductsGenerator
from app.generators.retail.stores import StoresGenerator
from app.utils.retail_metrics import recalculate_retail_totals


@dataclass(frozen=True, slots=True)
class RetailGenerationConfig:
    """Record counts for every generated retail table."""

    customers: int
    products: int
    stores: int
    orders: int
    order_items: int
    seed: int | None = None

    def __post_init__(self) -> None:
        if any(
            count < 1
            for count in (
                self.customers,
                self.products,
                self.stores,
                self.orders,
                self.order_items,
            )
        ):
            raise ValueError("all record counts must be at least 1")


class RetailDatasetGenerator:
    """Coordinate table generators while preserving referential integrity."""

    def __init__(self, config: RetailGenerationConfig) -> None:
        self._config = config
        context = GenerationContext.create(config.seed)
        self._customers = CustomersGenerator(context)
        self._products = ProductsGenerator(context)
        self._stores = StoresGenerator(context)
        self._orders = OrdersGenerator(context)
        self._order_items = OrderItemsGenerator(context)

    def generate(self) -> dict[str, pd.DataFrame]:
        """Generate all retail tables in dependency order."""
        customers = self._customers.generate(self._config.customers)
        products = self._products.generate(self._config.products)
        stores = self._stores.generate(self._config.stores)
        orders = self._orders.generate(self._config.orders, customers, stores)
        order_items = self._order_items.generate(
            self._config.order_items, orders, products
        )
        recalculate_retail_totals({"orders": orders, "order_items": order_items})

        return {
            "customers": customers,
            "products": products,
            "stores": stores,
            "orders": orders,
            "order_items": order_items,
        }
