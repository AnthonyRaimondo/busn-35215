import asyncio
import json
import time
from urllib.request import Request, urlopen
from datetime import date, timedelta, datetime

import aiohttp as aiohttp
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


def construct_payload(begin: date, filings_filter: str, forms_to_request: int, start_from: int) -> dict:
    SEC_PAYLOAD.get("query").get("query_string")["query"] = filings_filter.format(begin, begin)
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


async def download_file(session, url: str) -> BeautifulSoup:
    async with session.get(url) as response:
        content = await response.text()
        return BeautifulSoup(content, "lxml")


async def download_all_files(urls: list):
    auth_headers = {"Authorization": Config.SEC_API_KEY, "User-Agent": Config.SEC_USER_AGENT}
    async with aiohttp.ClientSession(headers=auth_headers) as session:
        tasks, requests_made = [], 0
        for url in urls:
            requests_made += 1
            task = asyncio.ensure_future(download_file(session, url))
            tasks.append(task)
            if requests_made == 9:
                await asyncio.sleep(1.2)
                requests_made = 0
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results


async def download_form_4_filings(begin: date, end: date, start_from: int = 0, existing_filing_urls: list = None) -> None:
    last_sleep = 0
    if begin > end:  # Base Case: date to start query from is after date to stop at
        return

    # Recursive Case: There are filings yet to be downloaded, continue consuming them

    # instantiate arrays to store urls for ensuring forms are not downloaded multiple times
    if existing_filing_urls is None:
        existing_filing_urls = []
    filing_urls_from_this_iteration = []

    # create payload to retrieve filing metadata
    size = 200  # 200 seems to be the max the SEC's api will return
    payload = construct_payload(begin, FORM_4_FILTER, size, start_from)

    # make request to SEC api with custom payload
    sec_response = call_sec_api(payload)

    # iterate over filings returned for the date range specified
    if len(sec_response.filings) > 0:
        for filing in sec_response.filings:
            # there should be some overlap of previous query end date and new query begin date, to ensure no filings are missed
            if filing.linkToFilingDetails not in existing_filing_urls:
                if filing.ticker is not None and len(filing.ticker) > 0:
                    existing_filing_urls.append(filing.linkToFilingDetails)
                    filing_urls_from_this_iteration.append(filing.linkToFilingDetails)
        responses = await download_all_files(filing_urls_from_this_iteration)
        for response in responses:
            consumer = consume_and_save_xml_form_4_filing  # if ".xml" in url else consume_and_save_txt_form_4_filing  # some older filings are only made available in .txt format
            try:
                consumer(response, filing.filedAt)
            except Exception as e:
                print(e)
                seconds_to_sleep = 60 * 10
                print(f"sleeping for {seconds_to_sleep} seconds due to exception. Time since last sleep: {time.time()-last_sleep}")
                last_sleep = time.time()
                time.sleep(seconds_to_sleep)

    # recursive call
    if len(sec_response.filings) < size:  # all filings for this date have been processed
        print(f"{begin} complete")
        new_begin_date = begin + timedelta(days=1)
        await download_form_4_filings(new_begin_date, end, 0, filing_urls_from_this_iteration)
    else:  # more filings left to process for this date
        await download_form_4_filings(begin, end, start_from + size, filing_urls_from_this_iteration)


if __name__ == "__main__":
    # begin_date = date(1999, 6, 1)  # inclusive - per SEC api
    begin_date = date(2021, 3, 24)  # inclusive - per SEC api
    end_date = date(2021, 6, 1)  # exclusive - per SEC api
    asyncio.get_event_loop().run_until_complete(download_form_4_filings(begin_date, end_date))
