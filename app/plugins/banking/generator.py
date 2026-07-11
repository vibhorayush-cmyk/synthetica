from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd
from faker import Faker


@dataclass(frozen=True, slots=True)
class BankingGenerationConfig:
    customers: int
    branches: int
    accounts: int
    transactions: int
    loans: int
    credit_cards: int
    payments: int
    seed: int | None = None


class BankingDatasetGenerator:
    """Generate banking tables with referential integrity."""

    def __init__(self, config: BankingGenerationConfig) -> None:
        self._config = config
        self._faker = Faker()
        self._faker.seed_instance(config.seed)
        self._rng = np.random.default_rng(config.seed)

    def generate(self) -> dict[str, pd.DataFrame]:
        customers = self._generate_customers()
        branches = self._generate_branches()
        accounts = self._generate_accounts(customers, branches)
        transactions = self._generate_transactions(accounts)
        loans = self._generate_loans(customers)
        credit_cards = self._generate_credit_cards(customers)
        payments = self._generate_payments(transactions)
        return {
            "customers": customers,
            "accounts": accounts,
            "branches": branches,
            "transactions": transactions,
            "loans": loans,
            "credit_cards": credit_cards,
            "payments": payments,
        }

    def _generate_customers(self) -> pd.DataFrame:
        rows = []
        for index in range(self._config.customers):
            dob = self._faker.date_of_birth(minimum_age=20, maximum_age=80)
            rows.append(
                {
                    "CustomerID": index + 1,
                    "Name": self._faker.name(),
                    "Gender": self._rng.choice(["M", "F", "Other"]),
                    "DOB": dob,
                    "Age": (datetime.now().date() - dob).days // 365,
                    "Occupation": self._rng.choice(
                        [
                            "Engineer",
                            "Teacher",
                            "Doctor",
                            "Manager",
                            "Analyst",
                            "Student",
                        ]
                    ),
                    "Income": round(float(self._rng.integers(40_000, 250_000)), 2),
                    "RiskCategory": self._rng.choice(["Low", "Medium", "High"]),
                    "City": self._faker.city(),
                    "State": self._faker.state(),
                    "Country": self._faker.country(),
                    "Email": self._faker.email(),
                    "Phone": self._faker.phone_number(),
                }
            )
        return pd.DataFrame(rows)

    def _generate_branches(self) -> pd.DataFrame:
        rows = []
        for index in range(1, self._config.branches + 1):
            rows.append(
                {
                    "BranchID": index,
                    "BranchName": f"Branch {index}",
                    "City": self._faker.city(),
                    "State": self._faker.state(),
                    "Country": self._faker.country(),
                }
            )
        return pd.DataFrame(rows)

    def _generate_accounts(
        self, customers: pd.DataFrame, branches: pd.DataFrame
    ) -> pd.DataFrame:
        rows = []
        for index in range(self._config.accounts):
            customer_id = int(customers.iloc[index % len(customers)]["CustomerID"])
            branch_id = int(branches.iloc[index % len(branches)]["BranchID"])
            rows.append(
                {
                    "AccountID": index + 1,
                    "CustomerID": customer_id,
                    "BranchID": branch_id,
                    "AccountType": self._rng.choice(["Savings", "Current", "Salary"]),
                    "Balance": round(float(self._rng.uniform(1000, 250000)), 2),
                    "OpenedDate": self._faker.date_between(
                        start_date="-5y", end_date="today"
                    ),
                    "Status": self._rng.choice(["Active", "Dormant", "Closed"]),
                }
            )
        return pd.DataFrame(rows)

    def _generate_transactions(self, accounts: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for index in range(self._config.transactions):
            account_id = int(accounts.iloc[index % len(accounts)]["AccountID"])
            rows.append(
                {
                    "TransactionID": index + 1,
                    "AccountID": account_id,
                    "TransactionDate": self._faker.date_between(
                        start_date="-1y", end_date="today"
                    ),
                    "TransactionType": self._rng.choice(
                        ["Deposit", "Withdrawal", "Transfer", "POS"]
                    ),
                    "Channel": self._rng.choice(["Branch", "ATM", "Online", "Mobile"]),
                    "Amount": round(float(self._rng.uniform(10, 5000)), 2),
                    "MerchantCategory": self._rng.choice(
                        ["Retail", "Travel", "Groceries", "Utilities", "Entertainment"]
                    ),
                    "Currency": self._rng.choice(["USD", "EUR", "GBP"]),
                    "Status": self._rng.choice(
                        ["Completed", "Pending", "Declined", "Chargeback"]
                    ),
                }
            )
        return pd.DataFrame(rows)

    def _generate_loans(self, customers: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for index in range(self._config.loans):
            customer_id = int(customers.iloc[index % len(customers)]["CustomerID"])
            rows.append(
                {
                    "LoanID": index + 1,
                    "CustomerID": customer_id,
                    "LoanType": self._rng.choice(
                        ["Personal", "Home", "Auto", "Education"]
                    ),
                    "Principal": round(float(self._rng.uniform(5000, 500000)), 2),
                    "InterestRate": round(float(self._rng.uniform(6.0, 15.0)), 2),
                    "EMI": round(float(self._rng.uniform(200, 6000)), 2),
                    "OutstandingBalance": round(
                        float(self._rng.uniform(1000, 400000)), 2
                    ),
                    "Status": self._rng.choice(["Active", "Closed", "Overdue"]),
                }
            )
        return pd.DataFrame(rows)

    def _generate_credit_cards(self, customers: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for index in range(self._config.credit_cards):
            customer_id = int(customers.iloc[index % len(customers)]["CustomerID"])
            rows.append(
                {
                    "CardID": index + 1,
                    "CustomerID": customer_id,
                    "CardType": self._rng.choice(["Classic", "Gold", "Platinum"]),
                    "CreditLimit": round(float(self._rng.uniform(1000, 10000)), 2),
                    "CurrentBalance": round(float(self._rng.uniform(0, 8000)), 2),
                    "Utilization": round(float(self._rng.uniform(0, 100)), 2),
                    "Status": self._rng.choice(["Active", "Blocked", "Closed"]),
                }
            )
        return pd.DataFrame(rows)

    def _generate_payments(self, transactions: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for index in range(self._config.payments):
            transaction_id = int(
                transactions.iloc[index % len(transactions)]["TransactionID"]
            )
            rows.append(
                {
                    "PaymentID": index + 1,
                    "TransactionID": transaction_id,
                    "PaymentMethod": self._rng.choice(["Card", "UPI", "ACH", "Cash"]),
                    "Amount": round(float(self._rng.uniform(10, 5000)), 2),
                    "SettlementStatus": self._rng.choice(
                        ["Settled", "Pending", "Failed"]
                    ),
                }
            )
        return pd.DataFrame(rows)
