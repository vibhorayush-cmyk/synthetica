"""Data dictionary generation for exported datasets."""

import pandas as pd


_COLUMN_DESCRIPTIONS = {
    "CustomerID": "Unique identifier for a customer.",
    "ProductID": "Unique identifier for a product.",
    "StoreID": "Unique identifier for a store.",
    "OrderID": "Unique identifier for an order.",
    "Name": "Customer full name.",
    "Email": "Customer email address.",
    "Phone": "Customer phone number.",
    "PostalCode": "Postal or ZIP code associated with the record.",
    "Gender": "Customer gender.",
    "Age": "Customer age in years.",
    "City": "City associated with the record.",
    "State": "State or region associated with the store.",
    "StoreName": "Retail store name.",
    "Country": "Country associated with the record.",
    "Category": "Product category.",
    "Brand": "Product brand.",
    "CostPrice": "Product acquisition cost per unit.",
    "SellingPrice": "Product selling price per unit.",
    "Currency": "Currency code for product prices.",
    "OrderDate": "Date on which the order was placed.",
    "PaymentMethod": "Method used to pay for the order.",
    "OrderChannel": "Channel through which the order was placed.",
    "OrderTotal": "Total net sales amount for the order.",
    "Quantity": "Number of product units in the order item.",
    "UnitPrice": "Selling price charged per unit.",
    "Discount": "Discount rate applied to the order item.",
    "SalesAmount": "Net sales amount after discount.",
    "IsReturned": "Whether the order item was returned.",
    "Profit": "Profit amount for the order item.",
}

_PRIMARY_KEYS = {
    "customers": "CustomerID",
    "products": "ProductID",
    "stores": "StoreID",
    "orders": "OrderID",
}

_FOREIGN_KEYS = {
    ("orders", "CustomerID"): "customers.CustomerID",
    ("orders", "StoreID"): "stores.StoreID",
    ("order_items", "OrderID"): "orders.OrderID",
    ("order_items", "ProductID"): "products.ProductID",
}


class DataDictionaryGenerator:
    """Build field-level documentation from dataset tables."""

    def generate(self, tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
        """Return a data dictionary for every column in every supplied table."""
        records: list[dict[str, str]] = []
        for table_name, dataframe in tables.items():
            primary_key = _PRIMARY_KEYS.get(table_name)
            for column_name, data_type in dataframe.dtypes.items():
                records.append(
                    {
                        "Table Name": table_name,
                        "Column Name": column_name,
                        "Data Type": str(data_type),
                        "Description": _COLUMN_DESCRIPTIONS.get(
                            column_name, f"{column_name} field for {table_name}."
                        ),
                        "Primary Key": "Yes" if column_name == primary_key else "No",
                        "Foreign Key": _FOREIGN_KEYS.get((table_name, column_name), ""),
                    }
                )
        return pd.DataFrame(
            records,
            columns=[
                "Table Name",
                "Column Name",
                "Data Type",
                "Description",
                "Primary Key",
                "Foreign Key",
            ],
        )
