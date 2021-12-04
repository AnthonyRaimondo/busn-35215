from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import pandas

from common.constant.consume import BEGIN_DATE, END_DATE
from common.constant.digest import RESOURCES_PATH


def load_csv(path: Path) -> pandas.DataFrame or None:
    try:
        return pandas.read_csv(f"{path}.csv").fillna(0).replace("None", 0)
    except FileNotFoundError:  # weekends and holidays
        return None
    except TypeError:
        return None


def load_open_market_transactions(start_from: date = BEGIN_DATE, stop_at: date = END_DATE) -> dict[date, pandas.DataFrame]:
    base_path = RESOURCES_PATH.joinpath("NonDerivativeTransactions")
    futures, relevant_transactions_dict = {}, {}
    with ThreadPoolExecutor() as executor:
        while start_from < stop_at:
            current_path = base_path.joinpath(str(start_from.year)).joinpath(str(start_from.month)).joinpath(str(start_from.day))
            futures[executor.submit(load_csv, current_path)] = start_from
            start_from += timedelta(days=1)
    for all_transactions_future in as_completed(futures):
        transactions_date = futures[all_transactions_future]
        all_transactions = all_transactions_future.result()
        if all_transactions is not None:
            relevant_transactions_dict[transactions_date] = all_transactions[all_transactions['transaction_code'].isin(["P", "S"])]
    return relevant_transactions_dict


def load_index_returns() -> pandas.DataFrame:
    index_returns = load_csv(RESOURCES_PATH.joinpath("daily-index-returns"))
    index_returns["DATE"] = pandas.to_datetime(index_returns["DATE"])
    return index_returns


def load_t_bill_rates() -> pandas.DataFrame:
    t_bill_returns = load_csv(RESOURCES_PATH.joinpath("t-bill-rates"))
    t_bill_returns["DATE"] = pandas.to_datetime(t_bill_returns["DATE"], format="%m/%d/%Y")
    return t_bill_returns


# if __name__ == "__main__":
#     asdf = load_open_market_transactions()
#     index_returns = load_index_returns()
#     print(index_returns.shape)
#     t_bill_returns = load_t_bill_returns()
#     print(t_bill_returns.shape)
#     rows = 0
#     for key, value in asdf.items():
#         rows += value.shape[0]
#     print(rows)
