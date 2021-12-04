COLUMNS = [
    "id",
    "date",
    "company_cik",
    "company_ticker",
    "shareholder_cik",
    "shareholder_name",
    "shareholder_title",
    "shareholder_director",
    "shareholder_ten_percent_owner",
    "shareholder_officer",
    "shareholder_other",
    "transaction_code",
    "number_of_shares",
    "shares_held_following_transaction",
    "share_price"
]
MEDIAN_SENTIMENT = -0.08111354227885599
TRADING_DAYS_PER_MONTH = 21
AVERAGE_DAYS_PER_MONTH = 30
MARGIN_LOAN_INTEREST_RATE = 0.04  # annual
HOLDING_PERIODS = [2, 3, 8, 12]
INSIDER_FILTERS = [
    'all',
    'director',
    'officer',
    'officer-director',
    'CEO',
    'CFO',
    'CEO-and-CFO',
    'chair',
    'CEO-and-chair',
    'exclude-large-shareholders',
    'ten-percent-owner'
]
