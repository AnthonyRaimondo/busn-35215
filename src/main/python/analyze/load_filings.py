import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import dask.dataframe as dd
import pandas

from common.constant.analyze import COLUMNS
from common.constant.consume import BEGIN_DATE, END_DATE
from common.constant.digest import RESOURCES_PATH


def load_csv(path: Path) -> pandas.DataFrame or None:
    try:
        return pandas.read_csv(f"{path}.csv")
    except FileNotFoundError:  # weekends and holidays
        return None


def load_open_market_transactions(start_from: date = BEGIN_DATE) -> pandas.DataFrame:
    start_time = time.time()
    base_path = RESOURCES_PATH.joinpath("NonDerivativeTransactions")
    futures, relevant_transactions_dict = {}, {}
    with ThreadPoolExecutor() as executor:
        while start_from < END_DATE:
            current_path = base_path.joinpath(str(start_from.year)).joinpath(str(start_from.month)).joinpath(str(start_from.day))
            futures[executor.submit(load_csv, current_path)] = start_from
            start_from += timedelta(days=1)
    for all_transactions_future in as_completed(futures):
        transactions_date = futures[all_transactions_future]
        all_transactions = all_transactions_future.result()
        if all_transactions is not None:
            open_market_transactions = all_transactions[all_transactions['transaction_code'].isin(["P", "S"])]
            open_market_transactions.insert(1, "date", transactions_date)
            open_market_transactions_dict = open_market_transactions.to_dict(orient='list')
            try:
                relevant_transactions_dict = {key: relevant_transactions_dict[key] + values for key, values in
                                              open_market_transactions_dict.items()}
            except KeyError:  # initialize the dictionary
                relevant_transactions_dict = open_market_transactions_dict
            # relevant_transactions = relevant_transactions.append(open_market_transactions, ignore_index=True)
    print(f"{round((time.time() - start_time) / 60, 2)} minutes")
    return pandas.DataFrame.from_dict(data=relevant_transactions_dict)


if __name__ == "__main__":
    print(load_open_market_transactions().shape)
