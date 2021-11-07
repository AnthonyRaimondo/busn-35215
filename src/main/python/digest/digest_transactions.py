import os
import uuid
from datetime import datetime
from typing import List, Dict

from common.constant.digest import BASE_FILE_PATH, TRANSACTION_ID
from digest.file_operations import prepare_file_structure
from domain.form_4_filing.filing_transactions import FilingTransactions
from domain.transaction import Transaction


def digest_transactions(filing_transactions: FilingTransactions, filing_date: datetime) -> None:
    if filing_transactions.non_derivative_transactions is not None and len(filing_transactions.non_derivative_transactions) > 0:
        format_and_save_transactions(filing_transactions.non_derivative_transactions, filing_date)
    if filing_transactions.derivative_transactions is not None and len(filing_transactions.derivative_transactions) > 0:
        format_and_save_transactions(filing_transactions.non_derivative_transactions, filing_date)


def format_and_save_transactions(transactions: List[Transaction], filing_date: datetime) -> None:
    transactions_dir = os.path.join(BASE_FILE_PATH, "main", "resources", f"{transactions[0].__class__.__name__}s")
    transactions_by_date = {}
    for transaction in transactions:
        if not os.path.exists(f"{transactions_dir}\\{filing_date.year}\\{filing_date.month}\\{filing_date.day}.csv"):
            prepare_file_structure(transactions_dir, filing_date, TRANSACTION_ID + "," + ",".join(list(transaction.__dict__.keys())))
        if filing_date not in transactions_by_date:
            transactions_by_date[filing_date] = []
        transactions_by_date[filing_date].append(f"{uuid.uuid4()},{','.join(str(value) for value in transaction.__dict__.values())}")
    save_transactions(transactions_by_date, transactions_dir)


def save_transactions(transactions_by_date: Dict[datetime, List[str]], transactions_dir: str) -> None:
    for date, transactions in transactions_by_date.items():
        filename = f"{transactions_dir}\\{date.year}\\{date.month}\\{date.day}.csv"
        with open(filename, "r") as existing_csv_file:
            contents = existing_csv_file.read()
        with open(filename, "w") as csv_file:
            csv_file.write(contents + "\n" + "\n".join(transactions))
