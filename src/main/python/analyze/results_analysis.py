import pandas

from common.constant.analyze import HOLDING_PERIODS, INSIDER_FILTERS, TRADING_DAYS_PER_MONTH
from common.constant.digest import RESOURCES_PATH


def summarize_results():
    for holding_period in HOLDING_PERIODS:
        for insider_filter in INSIDER_FILTERS:
            filename = f"{insider_filter}-results_{holding_period}-months"
            results = pandas.read_csv(RESOURCES_PATH.joinpath("output").joinpath(f"{filename}.csv"))
            results_subset = results.iloc[holding_period*TRADING_DAYS_PER_MONTH:-holding_period*TRADING_DAYS_PER_MONTH]
            returns = results_subset[['simple-index-strategy', 'contribution-to-portfolio-return']].sum(axis=0).to_list()
            beta = results['index-holding-period-return'].cov(results['slice-return']) / (results['index-holding-period-return'].std()**2)
            print(filename)
            print(f"Excess return: {returns[1] - returns[0]}")
            print(f"Max: {results['index-weight'].max()}")
            print(f"Min: {results['index-weight'].min()}")
            print(f"Beta: {beta}", "\n")


if __name__ == '__main__':
    summarize_results()
