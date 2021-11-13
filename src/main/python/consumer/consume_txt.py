from typing import List

import common.constant.consume as const
from common.formatting import format_date, format_transaction_code, format_share_count, format_dollar_amount, strip_formatting
from digest.digest_transactions import digest_transactions
from domain.form_4_filing.company import Company
from domain.form_4_filing.derivative_transaction import DerivativeTransaction
from domain.form_4_filing.filing_transactions import FilingTransactions
from domain.form_4_filing.non_derivative_transaction import NonDerivativeTransaction
from domain.form_4_filing.shareholder import Shareholder


def consume_and_save_txt_form_4_filing(txt_file_contents: str, filing_date_string: str) -> None:
    company = extract_company_info(txt_file_contents)
    shareholder = extract_shareholder_info(txt_file_contents)
    non_derivative_transactions = extract_non_derivative_transactions(txt_file_contents)
    # todo: uncomment the two lines below and pass derivative_transactions if interested in derivative transactions
    # derivative_transactions = extract_derivative_transactions(txt_file_contents)
    digest_transactions(FilingTransactions(company, shareholder, non_derivative_transactions), format_date(filing_date_string))


def extract_company_info(file_contents: str) -> Company:
    cik = extract_cik(file_contents.split(const.COMPANY_INFO_SECTION_TXT_FILE)[1].split(const.REPORTING_OWNER_SECTION_TXT_FILE)[0])
    ticker = extract_company_ticker(file_contents.split(const.ISSUER_NAME_AND_TICKER)[1].split(const.IRS_SSN)[0])
    return Company(cik, ticker)


def extract_cik(company_section_text: str) -> str:
    return company_section_text.split(const.CIK_IDENTIFIER)[1].split("\n")[0].replace("\t", "")


def extract_name(shareholder_section_text: str) -> str:
    return shareholder_section_text.split(const.CONFORMED_NAME)[1].split("\n")[0].replace("\t", "")


def extract_company_ticker(company_name_and_ticker: str) -> str:
    if "(" in company_name_and_ticker:
        temp_ticker = company_name_and_ticker.split("(")[1].split(")")[0]
        return temp_ticker.split(":")[1] if ":" in temp_ticker else temp_ticker
    else:
        for element in company_name_and_ticker.split("\n"):
            potential_ticker = element.strip()
            if not any(character in potential_ticker for character in const.SPECIAL_CHARS) and len(potential_ticker) >= 1:
                return potential_ticker


def extract_shareholder_info(file_contents: str) -> Shareholder:
    shareholder_info_section = file_contents.split(const.REPORTING_OWNER_SECTION_TXT_FILE)[1]
    cik = extract_cik(shareholder_info_section)
    name = extract_name(shareholder_info_section)
    shareholder_relationship = extract_shareholder_relationship(file_contents)
    director = const.DIRECTOR in shareholder_relationship
    ten_percent_owner = const.TEN_PERCENT_OWNER in shareholder_relationship
    officer = const.OFFICER in shareholder_relationship
    other = const.OTHER_RELATIONSHIP in shareholder_relationship
    if officer or other:
        title = extract_shareholder_title(file_contents)
    else:
        title = const.DIRECTOR if director else const.TEN_PERCENT_OWNER
    return Shareholder(cik, name, title, director, ten_percent_owner, officer, other)


def extract_shareholder_relationship(file_contents: str) -> list:
    relationships = []
    relationship_section = file_contents.split(const.RELATIONSHIP_HEADER)[1].split(const.INDIVIDUAL_OR_JOINT_FILING)[0].split("(Check all applicable)")[1]
    for relationship_option in const.RELATIONSHIP_OPTIONS:
        preceding_relationship_text = relationship_section.split(relationship_option)[0]
        if "[" in preceding_relationship_text:
            parenthetical_contents = preceding_relationship_text.split("]")[-2].split("[")[-1]
        else:
            parenthetical_contents = preceding_relationship_text.split(")")[-2].split("(")[-1]
        if "X" in parenthetical_contents:
            if relationship_option == const.OTHER_RELATIONSHIP_WITH_NEWLINE:
                relationships.append(const.OTHER_RELATIONSHIP)
            elif relationship_option == const.OFFICER_WITH_NEWLINE:
                relationships.append(const.OFFICER)
            else:
                relationships.append(relationship_option)
    return relationships


def extract_shareholder_title(file_contents: str) -> str:
    raw_title = file_contents.split(const.RELATIONSHIP_HEADER)[1].split(const.INDIVIDUAL_OR_JOINT_FILING)[0].split("(specify below)")[1]
    return raw_title.replace("\n", "").strip(" ").split("=")[0].split("7.")[0]


def extract_non_derivative_transactions(file_contents: str) -> List[NonDerivativeTransaction]:
    non_derivative_transactions = []
    table = file_contents.split(const.NON_DERIVATIVE_TABLE_TXT)[1].split("Table II")[0]
    if "|\n" in table:
        rows = table.split("|\n")
    else:
        rows = table.split("-\n")
    for row in rows:
        if "<S>" in row:
            transaction = extract_non_derivative_transaction_details(row)
            if transaction is not None:
                non_derivative_transactions.append(transaction)
    return non_derivative_transactions


def extract_non_derivative_transaction_details(transaction_row: str) -> NonDerivativeTransaction or None:
    if "|" in transaction_row:  # pipe delimited
        cells = transaction_row.split("|")
        transaction_code = strip_formatting(format_transaction_code(cells[2]))
        number_of_shares = format_share_count(cells[4])
        shares_held_following_transaction = format_share_count(cells[7])
        share_price = format_dollar_amount(cells[6].strip())
        return NonDerivativeTransaction(transaction_code, number_of_shares, shares_held_following_transaction, share_price)
    else:  # space delimited
        length = len(transaction_row.split("<C>")[0])  # find length between start of row and first <C> tag
        cells = transaction_row.split("\n")[-2][length:].split()
        if relevant_data_exists(transaction_row):  # if True, non-derivative transaction present
            transaction_code = strip_formatting(format_transaction_code(cells[1]))
            number_of_shares = format_share_count(cells[3])
            shares_held_following_transaction = format_share_count(cells[6])
            share_price = format_dollar_amount(cells[5].strip())
            return NonDerivativeTransaction(transaction_code, number_of_shares, shares_held_following_transaction, share_price)
        else:  # if False, no non-derivative transaction present
            return None


def relevant_data_exists(messy_text: str) -> bool:
    cleaned_text = messy_text.replace("<S>", "").replace("<C>", "").replace(" ", "").replace("-", "") \
        .replace("_", "").replace("\n", "").replace("\t", "")
    return len(cleaned_text) > 0


def extract_derivative_transactions(file_contents: str) -> List[DerivativeTransaction]:
    derivative_transactions = []
    return derivative_transactions
