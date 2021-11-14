import os
import uuid
from datetime import date
from typing import List, Dict

from common.constant.digest import BASE_FILE_PATH, TRANSACTION_ID
from digest.file_operations import prepare_file_structure
from domain.form_4_filing.company import Company
from domain.form_4_filing.filing_transactions import FilingTransactions
from domain.form_4_filing.shareholder import Shareholder
from domain.form_4_filing.transaction import Transaction


def digest_transactions(filing_transactions: FilingTransactions, filing_date: date) -> None:
    if filing_transactions.non_derivative_transactions is not None and len(filing_transactions.non_derivative_transactions) > 0:
        format_and_save_transactions(filing_transactions.company, filing_transactions.shareholder, filing_transactions.non_derivative_transactions, filing_date)
    if filing_transactions.derivative_transactions is not None and len(filing_transactions.derivative_transactions) > 0:
        format_and_save_transactions(filing_transactions.company, filing_transactions.shareholder, filing_transactions.derivative_transactions, filing_date)


def format_and_save_transactions(company: Company, shareholder: Shareholder, transactions: List[Transaction], filing_date: date) -> None:
    if len(transactions) > 0:
        transactions_dir = os.path.join(BASE_FILE_PATH, "main", "resources", f"{transactions[0].__class__.__name__}s")
        transactions_by_date = {}
        company_headers = [f"company_{header}" for header in list(company.__dict__.keys())]
        shareholder_headers = [f"shareholder_{header}" for header in list(shareholder.__dict__.keys())]
        company_values = [str(value) for value in company.__dict__.values()]
        shareholder_values = [str(value) for value in shareholder.__dict__.values()]
        transaction_headers = list(transactions[0].__dict__.keys())
        for transaction in transactions:
            if not os.path.exists(f"{transactions_dir}\\{filing_date.year}\\{filing_date.month}\\{filing_date.day}.csv"):
                prepare_file_structure(transactions_dir, filing_date,
                                       TRANSACTION_ID + "," + ",".join(company_headers + shareholder_headers + transaction_headers))
            if filing_date not in transactions_by_date:
                transactions_by_date[filing_date] = []
                transaction_values = [str(value) for value in transaction.__dict__.values()]
            transactions_by_date[filing_date].append(','.join([str(uuid.uuid4())] + company_values + shareholder_values + transaction_values))
        save_transactions(transactions_by_date, transactions_dir)


def save_transactions(transactions_by_date: Dict[date, List[str]], transactions_dir: str) -> None:
    for date_obj, transactions in transactions_by_date.items():
        filename = f"{transactions_dir}\\{date_obj.year}\\{date_obj.month}\\{date_obj.day}.csv"
        with open(filename, "r") as existing_csv_file:
            contents = existing_csv_file.read()
        with open(filename, "w") as csv_file:
            csv_file.write(contents + "\n" + "\n".join(transactions))
