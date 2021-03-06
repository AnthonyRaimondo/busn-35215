from datetime import date
from typing import Tuple, List

from bs4 import BeautifulSoup
from bs4.element import Tag

from common.constant import consume as const
from consumer.digest.digest_transactions import digest_transactions
from common.formatting import format_dollar_amount, format_share_count, format_transaction_code, strip_formatting
from domain.form_4_filing.company import Company
from domain.form_4_filing.derivative_transaction import DerivativeTransaction
from domain.form_4_filing.filing_transactions import FilingTransactions
from domain.form_4_filing.non_derivative_transaction import NonDerivativeTransaction
from domain.form_4_filing.shareholder import Shareholder


def consume_and_save_xml_form_4_filing(lxml: BeautifulSoup, filing_date: date) -> None:
    tables = lxml.findAll("table")
    for table in tables:
        if const.SHAREHOLDER_TABLE in table.text:
            company, shareholder = collect_transaction_meta_data(table)
        elif const.NON_DERIVATIVE_TABLE in table.text:
            non_derivative_transactions = collect_non_derivative_info(table)
        # todo: uncomment the two lines below and pass derivative_transactions if interested in derivative transactions
        # elif const.DERIVATIVE_TABLE in table.text:
        #     derivative_transactions = collect_derivative_info(table)
            break  # this table will always be the last one we're interested in
    try:
        digest_transactions(FilingTransactions(company, shareholder, non_derivative_transactions), filing_date)
    except UnboundLocalError:
        return None  # sometimes the SEC's format is incorrect or the file is unavailable


def collect_transaction_meta_data(table: Tag) -> Tuple[Company, Shareholder]:
    def extract_cik(row_tag_string: str) -> str:
        return row_tag_string.split(const.CIK)[1].split("\"")[0]  # keep as str to preserve preceding zeros

    def extract_shareholder_name(name_and_address: Tag) -> str:
        next_item_contains_name = False
        for element in name_and_address.contents:
            if next_item_contains_name:
                return element.text
            next_item_contains_name = const.NAME_HEADER in element.text

    def extract_shareholder_relationship(relationship_to_issuer: Tag) -> list:
        relationships = []
        for tr in relationship_to_issuer.findAll("tr"):
            next_item_contains_relationship = False
            for td in tr.findAll("td"):
                if next_item_contains_relationship:
                    relationships.append(td.text)
                next_item_contains_relationship = "X" in td.text
        return relationships

    def extract_shareholder_title(relationship_to_issuer: Tag) -> str:
        title_tag: Tag = relationship_to_issuer.findAll("tr")[-1]
        return title_tag.text

    def collect_company_info(company_and_ticker: Tag) -> Company:
        cik_number = extract_cik(str(company_and_ticker))
        cleaned_text = company_and_ticker.text.split(const.ISSUER_NAME_AND_TICKER)[1].split("\n")
        ticker = strip_formatting(cleaned_text[2].split("[")[1].split("]")[0].strip())
        return Company(cik_number, ticker)

    def collect_shareholder_info(name_and_address: Tag, relationship_to_issuer: Tag) -> Shareholder:
        cik_number = extract_cik(str(name_and_address))
        name = strip_formatting(extract_shareholder_name(name_and_address))
        shareholder_relationship = extract_shareholder_relationship(relationship_to_issuer.table)
        director = const.DIRECTOR in shareholder_relationship
        ten_percent_owner = const.TEN_PERCENT_OWNER in shareholder_relationship
        officer = const.OFFICER in shareholder_relationship
        other = const.OTHER_RELATIONSHIP in shareholder_relationship
        if officer or other:
            title = extract_shareholder_title(relationship_to_issuer.table)
        else:
            title = const.DIRECTOR if director else const.TEN_PERCENT_OWNER
        return Shareholder(cik_number, name, strip_formatting(title), director, ten_percent_owner, officer, other)

    for item in table.contents:
        if const.SHAREHOLDER_TABLE in item.text:
            relevant_rows = []
            for row in item.contents:
                if isinstance(row, Tag):
                    relevant_rows.append(row)
            company = collect_company_info(relevant_rows[1])
            shareholder = collect_shareholder_info(relevant_rows[0], relevant_rows[2])
            break

    return company, shareholder


def collect_non_derivative_info(table: Tag) -> List[NonDerivativeTransaction] or None:
    non_derivative_transactions = []
    tbody = table.find("tbody")
    if tbody is not None:
        for row in tbody.findAll("tr"):
            cells = row.findAll("td")
            if len(cells[5].text) > 0:  # number of shares will be null for indirect ownership disclosure
                number_of_shares = format_share_count(cells[5].text)
                if number_of_shares != 0.0:  # some transactions are not unitized; we are not interested in these
                    transaction_code = format_transaction_code(cells[3].text)
                    share_price = format_dollar_amount(cells[7].text)
                    shares_held_following_transaction = format_share_count(cells[8].text)
                    non_derivative_transactions.append(NonDerivativeTransaction(
                        transaction_code, number_of_shares, shares_held_following_transaction, share_price)
                    )
        return non_derivative_transactions
    else:
        return None


def collect_derivative_info(table: Tag) -> List[DerivativeTransaction] or None:
    derivative_transactions = []
    tbody = table.find("tbody")
    if tbody is not None:
        for row in tbody.findAll("tr"):
            cells = row.findAll("td")
            transaction_code = format_transaction_code(cells[4].text)
            if len(transaction_code) == 0:
                continue
            number_of_shares = format_share_count(cells[6].text if len(cells[6].text) > 0 else cells[7].text)
            shares_held_following_transaction = format_share_count(cells[13].text)
            share_price = format_dollar_amount(cells[12].text)
            exercise_price = format_dollar_amount(cells[1].text)
            derivative_transactions.append(DerivativeTransaction(
                transaction_code, number_of_shares, shares_held_following_transaction, share_price, exercise_price)
            )
        return derivative_transactions
    else:
        return None
