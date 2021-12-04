from datetime import date, timedelta

import pandas

from analyze.load_filings import load_open_market_transactions
from common.constant.consume import END_DATE
from common.constant.digest import RESOURCES_PATH


class TransactorSummary:
    def __init__(self, total_trades: int = 0, purchases: int = 0, shares_purchased: float = 0.0, sales: int = 0,
                 shares_sold: float = 0.0, cumulative_purchase_amount: float = 0.0, cumulative_sale_amount: float = 0.0):
        self.total_trades = total_trades
        self.purchases = purchases
        self.shares_purchased = shares_purchased
        self.sales = sales
        self.shares_sold = shares_sold
        self.cumulative_purchase_amount = cumulative_purchase_amount
        self.cumulative_sale_amount = cumulative_sale_amount

    def __add__(self, other):
        return TransactorSummary(
            self.total_trades + other.total_trades,
            self.purchases + other.purchases,
            self.shares_purchased + other.shares_purchased,
            self.sales + other.sales,
            self.shares_sold + other.shares_sold,
            self.cumulative_purchase_amount + other.cumulative_purchase_amount,
            self.cumulative_sale_amount + other.cumulative_sale_amount
        )

    def __radd__(self, other):
        return self + other

    def __repr__(self):
        return f"{self.total_trades},{self.purchases},{self.sales}," \
               f"${round(self.cumulative_purchase_amount/self.shares_purchased, 2)}," \
               f"${round(self.cumulative_sale_amount/self.shares_sold, 2)}"


def breakdown_of_insider_trades_by_type_of_transaction(all_transactions: dict, start_from: date) -> str:
    all_transactors, directors, officers, officer_directors, others, large_shareholders = tuple([TransactorSummary()]*6)
    while start_from < END_DATE:
        transactions = all_transactions.get(start_from)
        if transactions is not None and len(transactions.index) > 0:
            transactions.iloc[:, 6:9] = transactions.iloc[:, 6:9].astype('bool')
            transactions.iloc[:, -3:] = transactions.iloc[:, -3:].fillna(0).astype('float64').abs()
            transactions.loc[transactions["transaction_code"] == "S", "number_of_shares"] *= -1

            director = transactions.loc[transactions["shareholder_director"] & ~transactions["shareholder_officer"]]
            officer = transactions.loc[~transactions["shareholder_director"] & transactions["shareholder_officer"]]
            officer_director = transactions.loc[transactions["shareholder_director"] & transactions["shareholder_officer"]]
            ten_percent_owner = transactions.loc[transactions["shareholder_ten_percent_owner"] & ~transactions["shareholder_officer"] & ~transactions["shareholder_director"]]
            other = transactions.loc[transactions["shareholder_other"] & ~transactions["shareholder_officer"] & ~transactions["shareholder_director"] & ~transactions["shareholder_ten_percent_owner"]]

            all_transactors += create_transactor_summary(transactions)
            directors += create_transactor_summary(director)
            officers += create_transactor_summary(officer)
            officer_directors += create_transactor_summary(officer_director)
            large_shareholders += create_transactor_summary(ten_percent_owner)
            others += create_transactor_summary(other)

        start_from += timedelta(days=1)

    return f"Type of Transactor,Total Trades,Number of Purchases,Number of Sales,Average Size of Purchase,Average Size of Sale\n" \
           f"All,{all_transactors}\nDirectors,{directors}\nOfficers,{officers}\nOfficer-Directors,{officer_directors}\n" \
           f"10% Owners,{large_shareholders}\nOthers,{others}"


def create_transactor_summary(df: pandas.DataFrame) -> TransactorSummary:
    total_trades = df.shape[0]
    purchases = df.loc[df["transaction_code"] == "P"]
    shares_purchased = sum(purchases["number_of_shares"])
    cumulative_purchase_amount = sum(purchases["number_of_shares"] * purchases["share_price"])
    sales = df.loc[df["transaction_code"] == "S"]
    shares_sold = sum(sales["number_of_shares"])
    cumulative_sale_amount = sum(sales["number_of_shares"] * sales["share_price"])
    return TransactorSummary(total_trades, purchases.shape[0], shares_purchased, sales.shape[0], shares_sold,
                             cumulative_purchase_amount, cumulative_sale_amount)


def historical_trade_volumes(all_transactions: dict, start_from: date, transaction_type: str = None) -> str:
    monthly_trades = {}
    while start_from < END_DATE:
        transactions = all_transactions.get(start_from)
        if transactions is not None and len(transactions.index) > 0:
            header = f"{start_from.month if start_from.month >= 10 else '0'+str(start_from.month)}/{start_from.year}"
            if header not in monthly_trades:
                monthly_trades[header] = 0
            if transaction_type is None:
                volume = transactions
            else:
                volume = transactions[transactions["transaction_code"] == transaction_type]
            monthly_trades[header] += len(volume.index)
        start_from += timedelta(days=1)
    return "\n".join(f"{month_header},{transaction_count}" for month_header, transaction_count in monthly_trades.items())


if __name__ == "__main__":
    insider_transactions = load_open_market_transactions()
    starting_date = date(2003, 6, 1)
    # breakdown = breakdown_of_insider_trades_by_type_of_transaction(insider_transactions, starting_date)
    # with open(RESOURCES_PATH.joinpath("data-summary.csv"), 'w+') as file:
    #     file.write(breakdown)
    trading_history = historical_trade_volumes(insider_transactions, starting_date)
    with open(RESOURCES_PATH.joinpath("transaction-volume.csv"), 'w+') as file:
        file.write(trading_history)
    sale_history = historical_trade_volumes(insider_transactions, starting_date, 'S')
    with open(RESOURCES_PATH.joinpath("sale-volume.csv"), 'w+') as file:
        file.write(sale_history)
    buy_history = historical_trade_volumes(insider_transactions, starting_date, 'P')
    with open(RESOURCES_PATH.joinpath("purchase-volume.csv"), 'w+') as file:
        file.write(buy_history)
