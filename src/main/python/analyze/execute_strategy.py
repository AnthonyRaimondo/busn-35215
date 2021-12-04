# import os
from copy import copy
from datetime import timedelta, date
from math import tanh
# from multiprocessing import Pool

from pandas import DataFrame

from analyze.load_filings import load_index_returns, load_t_bill_rates, load_open_market_transactions
from common.constant import analyze as const
from common.constant.consume import END_DATE
from common.constant.digest import RESOURCES_PATH


def orchestrate_strategy(insider_transactions: dict, daily_index_returns: DataFrame, daily_t_bill_rates: DataFrame,
                         holding_period: int, start_from: date, filter_for: str) -> None:
    filename = f"{filter_for}-results_{holding_period}-months"
    print(f"Working on: {filename}")
    turnover_period, non_trading_day_transactions = const.TRADING_DAYS_PER_MONTH * holding_period, None
    relevant_transactions = filter_insider_transactions(insider_transactions, filter_for)
    portfolio = DataFrame(columns=['date-opened', 'date-closed', 'days-remaining', 't-bill-ytm', 't-bill-weight',
                                   'index-weight', 'index-daily-return', 'index-holding-period-return',
                                   'slice-return', 'contribution-to-portfolio-return', 'simple-index-strategy'])
    matured_slices = copy(portfolio)
    while start_from < END_DATE + timedelta(days=holding_period*const.AVERAGE_DAYS_PER_MONTH):  # add turnover period to end so final slice returns are captured
        transactions = relevant_transactions.get(start_from)
        if transactions is not None and not transactions.empty:
            if non_trading_day_transactions is not None:  # still consider transactions that were filed on weekends and holidays
                transactions = transactions.append(non_trading_day_transactions, ignore_index=True)
                non_trading_day_transactions = None

            # gather market returns for this date
            date_selector = start_from.strftime("%Y-%m-%d 00:00:00")
            index_return = get_index_return(date_selector, daily_index_returns)
            t_bill_rate = get_t_bill_rate(date_selector, daily_t_bill_rates)

            # some form 4's aren't filed until the weekend or on a holiday, combine these transactions with the next trading day's
            if index_return is not None and t_bill_rate is not None:
                portfolio['days-remaining'] -= 1
                mature_slice = portfolio[portfolio['days-remaining'] == 0]

                # compute returns and retire oldest slice
                if not mature_slice.empty:
                    mature_slice_dict = add_mature_slice_return(mature_slice, holding_period, turnover_period, start_from)
                    mature_slice_index = int(mature_slice.index.values[0])
                    matured_slices = matured_slices.append(mature_slice_dict, ignore_index=True)
                    portfolio.drop(index=mature_slice_index, inplace=True)

                # get prevailing returns
                portfolio['index-holding-period-return'] += index_return
                percent_invested = (len(portfolio.index)+1) / turnover_period
                t_bill_ytm = compute_ytm(t_bill_rate)

                # 1-month T-bill may have matured for some slice(s). Invest in a new one at the prevailing rate
                days_to_renew_t_bill_investment_for = portfolio[portfolio['days-remaining'].isin([day for day in range(turnover_period) if day % const.TRADING_DAYS_PER_MONTH == 0])]
                if not days_to_renew_t_bill_investment_for.empty:
                    portfolio.loc[days_to_renew_t_bill_investment_for.index.values, 't-bill-ytm'] += t_bill_ytm

                # create and add new slice. No need to create new slices while observing returns for final slice (where start_from >= END_DATE)
                if start_from < END_DATE:
                    transactions.iloc[:, -3:] = transactions.iloc[:, -3:].astype('float64').abs()
                    aggregate_sentiment = compute_aggregate_insider_sentiment(transactions)
                    portfolio_slice = create_new_slice(start_from, turnover_period, aggregate_sentiment, index_return,
                                                       t_bill_ytm, percent_invested if percent_invested <= 1.0 else 1.0)
                    portfolio = portfolio.append(portfolio_slice, ignore_index=True)
            else:
                non_trading_day_transactions = transactions
        start_from += timedelta(days=1)
    matured_slices.to_csv(RESOURCES_PATH.joinpath("output").joinpath(f"{filename}.csv"))


def compute_aggregate_insider_sentiment(transactions: DataFrame) -> float:
    groups = transactions.groupby("shareholder_cik")
    cumulative_sentiment, insiders_with_zero_beginning_shares = 0, 0
    for _cik, group in groups:
        insider_sentiment = compute_individual_insider_sentiment(group)
        if insider_sentiment is not None:
            cumulative_sentiment += insider_sentiment
        else:
            insiders_with_zero_beginning_shares += 1
    total_insiders = len(groups) - insiders_with_zero_beginning_shares
    return cumulative_sentiment / total_insiders if total_insiders > 0 else 1.0  # neutral weighting


def create_new_slice(slice_date: date, turnover_period: int, aggregate_sentiment: float, index_return: float,
                     t_bill_ytm: float, percent_invested: float) -> dict:
    t_bill_weight = 1-aggregate_sentiment if aggregate_sentiment < 1.0 else 0.0
    return {'date-opened': slice_date, 'date-closed': None, 'days-remaining': turnover_period,
            'index-weight': aggregate_sentiment, 't-bill-ytm': t_bill_ytm, 't-bill-weight': t_bill_weight,
            'index-holding-period-return': 0.0, 'index-daily-return': index_return, 'slice-return': 0.0,
            'contribution-to-portfolio-return': 0.0, 'simple-index-strategy': index_return * percent_invested}


def compute_individual_insider_sentiment(insider_transactions: DataFrame) -> float or None:
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
            return tanh(sentiment-const.MEDIAN_SENTIMENT) + 1
        else:
            return None
    else:
        return None


def get_index_return(date_selector: str, index_returns: DataFrame) -> float or None:
    try:
        return float(index_returns[index_returns["DATE"] == date_selector]['ewretx'].iloc[0])
    except IndexError:
        return None


def get_t_bill_rate(date_selector: str, t_bill_rates: DataFrame) -> float or None:
    try:
        return float(t_bill_rates[t_bill_rates["DATE"] == date_selector]['one-month-rate'].iloc[0])
    except IndexError:
        return None


def compute_ytm(t_bill_rate: float) -> float:
    return ((t_bill_rate / 100) * 30) / 365


def add_mature_slice_return(mature_slice: DataFrame, holding_period: int, turnover_period: int, closing_date: date) -> dict:
    mature_slice_dict = mature_slice.iloc[0].to_dict()
    mature_slice_dict['date-closed'] = closing_date
    mature_slice_dict['t-bill-ytm'] /= holding_period
    slice_return = compute_slice_return(mature_slice_dict)
    mature_slice_dict['slice-return'] = slice_return
    mature_slice_dict['contribution-to-portfolio-return'] = slice_return / turnover_period
    return mature_slice_dict


def compute_slice_return(mature_slice_dict: dict) -> float:
    slice_term = (mature_slice_dict['date-closed'] - mature_slice_dict['date-opened']).days
    interest_charge = deduct_margin_loan_interest(slice_term, mature_slice_dict['index-weight'])
    return (mature_slice_dict['t-bill-weight'] * mature_slice_dict['t-bill-ytm']) + \
           (mature_slice_dict['index-weight'] * mature_slice_dict['index-holding-period-return']) - interest_charge


def deduct_margin_loan_interest(term: int, index_weight: float) -> float:
    if index_weight > 1.0:
        leverage_used = index_weight - 1.0
        leverage_ratio = leverage_used / index_weight  # index weight is the whole slice
    else:
        leverage_ratio = 0.0
    return ((const.MARGIN_LOAN_INTEREST_RATE / 365) * term) * leverage_ratio


def filter_insider_transactions(insider_transactions_dict: dict, filter_for: str) -> dict:
    """
    Filters for group of insiders to do analysis on
    :param insider_transactions_dict:
    :param filter_for: Group indicator enumerator
        Options Are:
            - 'all': All Filers
            - 'director': Directors
            - 'officer': Officers
            - 'officer-director': Officer-Directors
            - 'CEO': CEOs
            - 'CFO': CFOs
            - 'CEO-and-CFO': CEOs and CFOs
            - 'chair': Board Chairperson
            - 'CEO-and-chair': CEO and Chairperson
            - 'exclude-large-shareholders': Excluding Large Shareholders
            - 'ten-percent-owner': Only Large Shareholders
    :return: pandas DataFrame with relevant transactions
    """
    if filter_for == 'all':
        return insider_transactions_dict
    else:
        relevant_transactions = {}
        for transactions_date, transactions in insider_transactions_dict.items():
            transactions.iloc[:, 5] = transactions.iloc[:, 5].astype(str).fillna("")
            if filter_for == 'director':
                relevant_transactions[transactions_date] = transactions[transactions[f"shareholder_director"] & ~transactions["shareholder_officer"] & ~transactions["shareholder_ten_percent_owner"]]
            elif filter_for == 'officer':
                relevant_transactions[transactions_date] = transactions[transactions[f"shareholder_officer"] & ~transactions["shareholder_director"] & ~transactions["shareholder_ten_percent_owner"]]
            elif filter_for == 'ten-percent-owner':
                relevant_transactions[transactions_date] = transactions[transactions[f"shareholder_ten_percent_owner"] & ~transactions["shareholder_director"] & ~transactions["shareholder_officer"]]
            elif filter_for == 'officer-director':
                relevant_transactions[transactions_date] = transactions[transactions["shareholder_officer"] & transactions["shareholder_director"]]
            elif filter_for == 'CEO':
                relevant_transactions[transactions_date] = transactions[transactions['shareholder_title'].str.contains("CEO|Chief Executive Officer|C.E.O")]
            elif filter_for == 'CFO':
                relevant_transactions[transactions_date] = transactions[transactions['shareholder_title'].str.contains("CFO|Chief Financial Officer|C.F.O")]
            elif filter_for == 'CEO-and-CFO':
                relevant_transactions[transactions_date] = transactions[transactions['shareholder_title'].str.contains("CEO|Chief Executive Officer|C.E.O|CFO|Chief Financial Officer|C.F.O")]
            elif filter_for == 'chair':
                relevant_transactions[transactions_date] = transactions[transactions['shareholder_title'].str.contains("Chair|chair")]
            elif filter_for == 'CEO-and-chair':
                relevant_transactions[transactions_date] = transactions[transactions['shareholder_title'].str.contains("CEO|Chief Executive Officer|C.E.O|Chair|chair")]
            elif filter_for == 'exclude-large-shareholders':
                relevant_transactions[transactions_date] = transactions[transactions[f"shareholder_director"] | transactions["shareholder_officer"] | transactions["shareholder_other"]]
            else:
                print(f"Unknown filter applied: '{filter_for}'. Returning all insider transactions")
                filter_insider_transactions(insider_transactions_dict, filter_for='all')
        return relevant_transactions


if __name__ == "__main__":
    starting_date, stopping_date = date(2004, 6, 1), date(2021, 11, 25)  # collect enough transactions beyond the stop date to keep from "None" issues
    all_transactions = load_open_market_transactions(starting_date, stopping_date)
    all_index_returns, all_t_bill_rates = load_index_returns(), load_t_bill_rates()
    # todo: with Pool(processes=os.cpu_count()) as pool:
    for months_to_hold in const.HOLDING_PERIODS:
        for insider_filter in const.INSIDER_FILTERS:
            orchestrate_strategy(insider_transactions=all_transactions,
                                 daily_index_returns=all_index_returns,
                                 daily_t_bill_rates=all_t_bill_rates,
                                 holding_period=months_to_hold,
                                 start_from=starting_date,
                                 filter_for=insider_filter)
