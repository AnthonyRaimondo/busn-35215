import json
import os
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
from datetime import date, timedelta, datetime

import requests
from bs4 import BeautifulSoup

from common.config.app_config import Config
from common.constant.consume import FORM_4_FILTER, API, ENCODING, SEC_PAYLOAD
from consumer.consume_txt import consume_and_save_txt_form_4_filing
from consumer.consume_xml import consume_and_save_xml_form_4_filing
from domain.filings_metadata.filings_metadata import FilingsMetadata


def create_request(bytes_length: int) -> Request:
    request = Request(API)
    request.add_header('Authorization', Config.SEC_API_KEY)
    request.add_header('Content-Type', 'application/json; charset=' + ENCODING)
    request.add_header('Content-Length', bytes_length)
    return request


def construct_payload(begin: date, end: date, filings_filter: str, forms_to_request: int, start_from: int) -> dict:
    SEC_PAYLOAD.get("query").get("query_string")["query"] = filings_filter.format(begin, end)
    SEC_PAYLOAD["size"] = forms_to_request
    SEC_PAYLOAD["from"] = start_from
    return SEC_PAYLOAD


def call_sec_api(request_body: dict) -> FilingsMetadata:
    json_payload = json.dumps(request_body)
    payload_bytes = json_payload.encode(ENCODING)
    request = create_request(len(payload_bytes))
    response = urlopen(request, payload_bytes)
    response_body = response.read()
    return FilingsMetadata(**json.loads(response_body.decode(ENCODING)))


def _format_date(date_string: str) -> date:
    return datetime.strptime(date_string.split('-04:00')[0], "%Y-%m-%dT%H:%M:%S").date()


def download_file(url: str) -> BeautifulSoup:
    auth_headers = {
        "Authorization": Config.SEC_API_KEY,
        "User-Agent": Config.SEC_USER_AGENT,
    }
    response = requests.get(url, headers=auth_headers)
    decoded_content = response.content.decode(ENCODING)
    return BeautifulSoup(decoded_content, "lxml")


def download_form_4_filings(begin: date, end: date, start_from: int = 0, existing_filing_urls: list = None) -> None:
    if begin > end:  # Base Case: date to start query from is after date to stop at
        return

    # Recursive Case: There are filings yet to be downloaded, continue consuming them

    # instantiate arrays to store urls for ensuring forms are not downloaded multiple times
    if existing_filing_urls is None:
        existing_filing_urls = []
    filing_urls_from_this_iteration = []

    # create payload to retrieve filing metadata
    size = 200  # 200 seems to be the max the SEC's api will return
    payload = construct_payload(begin, end, FORM_4_FILTER, size, start_from)

    # make request to SEC api with custom payload
    sec_response = call_sec_api(payload)

    # iterate over filings returned for the date range specified
    for filing in sec_response.filings:
        # there should be some overlap of previous query end date and new query begin date, to ensure no filings are missed
        if filing.linkToFilingDetails not in existing_filing_urls:
            if len(filing.ticker) > 0:
                existing_filing_urls.append(filing.linkToFilingDetails)
                filing_urls_from_this_iteration.append(filing.linkToFilingDetails)
    url_content_mapping = {}
    with ThreadPoolExecutor() as executor:
        for url in filing_urls_from_this_iteration:
            future = executor.submit(download_file, url)
            url_content_mapping[url] = future.result()
    for url, content in url_content_mapping.items():
        consumer = consume_and_save_xml_form_4_filing if ".xml" in url else consume_and_save_txt_form_4_filing  # some older filings are only made available in .txt format
        consumer(content, filing.filedAt)
    latest_filing_date = _format_date(filing.filedAt)

    # recursive call
    if len(sec_response.filings) < size:  # all filings for this date have been processed
        print(f"{latest_filing_date} complete")
        print(latest_filing_date + timedelta(days=1))
        download_form_4_filings(latest_filing_date + timedelta(days=1), end, 0, filing_urls_from_this_iteration)
    else:  # more filings left to process for this date
        download_form_4_filings(latest_filing_date, end, start_from + size, filing_urls_from_this_iteration)


if __name__ == "__main__":
    # begin_date = date(1999, 6, 1)  # inclusive - per SEC api
    begin_date = date(2018, 6, 4)  # inclusive - per SEC api
    end_date = date(2021, 6, 1)  # exclusive - per SEC api
    download_form_4_filings(begin_date, end_date)
