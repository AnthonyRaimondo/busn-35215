from datetime import timedelta, date
from math import tanh

import pandas

from analyze.load_filings import load_index_returns, load_t_bill_returns, load_open_market_transactions
from common.constant.analyze import MEDIAN_SENTIMENT
from common.constant.consume import END_DATE


def compute_returns(start_from: date):
    insider_transactions = load_open_market_transactions()
    index_returns, t_bill_returns = load_index_returns(), load_t_bill_returns()
    while start_from < END_DATE:
        transactions = insider_transactions.get(start_from)
        if transactions is not None and transactions.shape[0] > 0:
            transactions.iloc[:, -3:] = transactions.iloc[:, -3:].astype('float64').abs()
            print(compute_aggregate_insider_sentiment(transactions))
        start_from += timedelta(days=1)


def compute_aggregate_insider_sentiment(transactions: pandas.DataFrame) -> float:
    groups = transactions.groupby("shareholder_cik")
    cumulative_sentiment, insiders_with_zero_beginning_shares = 0, 0
    for cik, group in groups:
        insider_sentiment = compute_individual_insider_sentiment(group)
        if insider_sentiment is not None:
            cumulative_sentiment += insider_sentiment
        else:
            insiders_with_zero_beginning_shares += 1
    return cumulative_sentiment / (len(groups) - insiders_with_zero_beginning_shares)


def compute_individual_insider_sentiment(insider_transactions: pandas.DataFrame) -> float or None:
    first_transaction = insider_transactions.iloc[0]
    if first_transaction["transaction_code"] == "S":
        initial_shares = first_transaction["shares_held_following_transaction"] + first_transaction["number_of_shares"]
    else:
        initial_shares = first_transaction["shares_held_following_transaction"] - first_transaction["number_of_shares"]
    if initial_shares > 0:
        last_transaction = insider_transactions.iloc[-1]
        ending_shares = last_transaction["shares_held_following_transaction"]

        # multiply shares transacted by -1 if transaction_code = "S"
        insider_transactions.loc[insider_transactions["transaction_code"] == "S", "number_of_shares"] *= -1
        insider_transaction_totals = insider_transactions.sum()
        shares_transacted_on_open_market = insider_transaction_totals["number_of_shares"]

        # account for any transactions that did not occur through open market purchase/sale
        shares_transacted_through_other_means = ending_shares - initial_shares - shares_transacted_on_open_market
        total_portfolio_base = initial_shares + shares_transacted_through_other_means
        if total_portfolio_base > 0:
            sentiment = shares_transacted_on_open_market / total_portfolio_base
            return tanh(sentiment-MEDIAN_SENTIMENT) + 1
        else:
            return None
    else:
        return None


if __name__ == "__main__":
    compute_returns(date(2004, 6, 1))
