from typing import List

from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
import requests

from config.app_config import Config
from constant import consumption_constants as const
from domain.form_4_filing.company import Company
from domain.form_4_filing.shareholder import Shareholder


def consume_and_save_xml_form_4_filing(url: str) -> None:
    auth_headers = {
        "Authorization": Config.SEC_API_KEY,
        "User-Agent": Config.SEC_USER_AGENT,
    }
    response = requests.get(url, headers=auth_headers)
    decoded_content = response.content.decode(const.ENCODING)
    lxml = BeautifulSoup(decoded_content, "lxml")
    for table in lxml.findAll("table"):
        if const.SHAREHOLDER_TABLE in table.text:
            company, shareholder = collect_transaction_meta_data(table)
        elif const.NON_DERIVATIVE_TABLE in table.text:
            collect_non_derivative_info(table)
        elif const.DERIVATIVE_TABLE in table.text:
            collect_derivative_info(table)
            break  # this table will always be the last one we're interested in


def collect_transaction_meta_data(table: Tag) -> tuple:
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
        company_name = cleaned_text[1].strip()
        ticker = cleaned_text[2].split("[")[1].split("]")[0].strip()
        return Company(cik_number, ticker, company_name)

    def collect_shareholder_info(name_and_address: Tag, relationship_to_issuer: Tag) -> Shareholder:
        cik_number = extract_cik(str(name_and_address))
        name = extract_shareholder_name(name_and_address)
        shareholder_relationship = extract_shareholder_relationship(relationship_to_issuer.table)
        director = const.DIRECTOR in shareholder_relationship
        ten_percent_owner = const.TEN_PERCENT_OWNER in shareholder_relationship
        officer = const.OFFICER in shareholder_relationship
        other = const.OTHER_RELATIONSHIP in shareholder_relationship
        if officer or other:
            title = extract_shareholder_title(relationship_to_issuer.table)
        else:
            title = const.DIRECTOR if director else const.TEN_PERCENT_OWNER
        return Shareholder(cik_number, name, title, director, ten_percent_owner, officer, other)

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


def collect_non_derivative_info(table: Tag):
    pass


def collect_derivative_info(table: Tag):
    pass
