from __future__ import annotations

import pandas as pd

from app.scenarios.base import BaseScenario


class NoneScenario(BaseScenario):
    name = "none"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        return dataset


class FraudSpikeScenario(BaseScenario):
    name = "fraud_spike"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        transactions = dataset["transactions"].copy()
        transactions.loc[
            transactions.index[: max(1, len(transactions) // 10)], "Status"
        ] = "Chargeback"
        dataset["transactions"] = transactions
        payments = dataset["payments"].copy()
        payments.loc[
            payments.index[: max(1, len(payments) // 8)], "SettlementStatus"
        ] = "Failed"
        dataset["payments"] = payments
        return dataset


class InterestRateHikeScenario(BaseScenario):
    name = "interest_rate_hike"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        loans = dataset["loans"].copy()
        loans.loc[:, "EMI"] = loans["EMI"] * 1.15
        loans.loc[:, "Status"] = loans["Status"].replace({"Active": "Active"})
        dataset["loans"] = loans
        return dataset


class LoanDefaultWaveScenario(BaseScenario):
    name = "loan_default_wave"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        loans = dataset["loans"].copy()
        loans.loc[loans.index[: max(1, len(loans) // 5)], "Status"] = "Overdue"
        dataset["loans"] = loans
        return dataset


class HolidaySpendingScenario(BaseScenario):
    name = "holiday_spending"

    def apply(self, dataset: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
        transactions = dataset["transactions"].copy()
        transactions.loc[
            transactions.index[: max(1, len(transactions) // 5)], "MerchantCategory"
        ] = "Entertainment"
        dataset["transactions"] = transactions
        return dataset
