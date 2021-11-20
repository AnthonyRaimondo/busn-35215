import os
from datetime import date


def prepare_file_structure(transactions_dir: str, transaction_date: date, csv_file_header: str) -> None:
    if not os.path.exists(transactions_dir):
        os.mkdir(transactions_dir)
    year, month, day = str(transaction_date.year), str(transaction_date.month), str(transaction_date.day)
    if not os.path.exists(f"{transactions_dir}\\{year}"):
        create_new_dir(transactions_dir, year)
    if not os.path.exists(f"{transactions_dir}\\{year}\\{month}"):
        create_new_dir(f"{transactions_dir}\\{year}", month)
    create_new_txt_file(f"{transactions_dir}\\{year}\\{month}", day, csv_file_header)


def create_new_dir(parent_dir: str, folder: str) -> None:
    os.mkdir(f"{parent_dir}\\{folder}")


def create_new_txt_file(parent_dir: str, filename: str, csv_file_header: str) -> None:
    with open(f"{parent_dir}\\{filename}.csv", "w+") as new_csv:
        new_csv.write(csv_file_header)
