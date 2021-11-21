import re


def format_dollar_amount(raw_dollar_string: str) -> float or None:
    if re.match(r"\((\d+)\)", raw_dollar_string):
        return None
    if "(" in raw_dollar_string:
        raw_dollar_string = raw_dollar_string.split("(")[0]
    clean_dollar_string = raw_dollar_string.replace("$", "").replace("\n", "").replace(",", "")
    if len(clean_dollar_string) > 0:
        return float(clean_dollar_string)
    else:
        return None


def format_share_count(shares_string: str) -> float or None:
    try:
        return float(shares_string.split("(")[0].replace(",", "").replace("\n", ""))
    except ValueError:  # sometimes this is given in dollars, not interested in these funds
        return None


def format_transaction_code(transaction_code_string: str) -> str:
    return transaction_code_string.split("(")[0].replace("\n", "")


def strip_formatting(input_string: str) -> str:
    return re.sub(r"\s+", " ", input_string.replace(",", "").replace("\n", "").replace("\t", "")).strip()
