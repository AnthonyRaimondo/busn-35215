import json
from urllib.request import Request, urlopen
from datetime import date

from config.app_config import Config
from constant.consumption_constants import FORM_4_FILTER, API, ENCODING, SEC_PAYLOAD
from consumer.consume_txt import consume_and_save_txt_form_4_filing
from consumer.consume_xml import consume_and_save_xml_form_4_filing
from domain.filings_metadata.filings_metadata import FilingsMetadata


def create_request(bytes_length: int) -> Request:
    request = Request(API)
    request.add_header('Authorization', Config.SEC_API_KEY)
    request.add_header('Content-Type', 'application/json; charset=' + ENCODING)
    request.add_header('Content-Length', bytes_length)
    return request


def construct_payload(begin: date, end: date, filings_filter: str, forms_to_request: int) -> dict:
    SEC_PAYLOAD.get("query").get("query_string")["query"] = filings_filter.format(begin, end)
    SEC_PAYLOAD["size"] = forms_to_request
    return SEC_PAYLOAD


def call_sec_api(request_body: dict) -> FilingsMetadata:
    json_payload = json.dumps(request_body)
    payload_bytes = json_payload.encode(ENCODING)
    request = create_request(len(payload_bytes))
    response = urlopen(request, payload_bytes)
    response_body = response.read()
    return FilingsMetadata(**json.loads(response_body.decode(ENCODING)))


def download_form_4_filings(begin: date, end: date, existing_filing_ids: list = None) -> None:
    if begin > end:  # Base Case: date to start query from is after date to stop at
        return

    # Recursive Case: There are filings yet to be downloaded, continue consuming them

    # instantiate arrays to store ids for ensuring forms are not downloaded multiple times
    if existing_filing_ids is None:
        existing_filing_ids = []
    filing_ids_from_this_iteration = []

    # create payload to retrieve filing metadata
    size = 200  # 200 seems to be the max the SEC's api will return
    payload = construct_payload(begin_date, end_date, FORM_4_FILTER, size)

    # make request to SEC api with custom payload
    sec_response = call_sec_api(payload)

    # iterate over filings returned for the date range specified
    for filing in sec_response.filings:
        # there should be some overlap of previous query end date and new query begin date, to ensure no filings are missed
        if filing.id not in existing_filing_ids:
            existing_filing_ids.append(filing.id)
            filing_ids_from_this_iteration.append(filing.id)
            if ".xml" not in filing.linkToFilingDetails:  # some older filings are only made available in .txt format
                consume_and_save_txt_form_4_filing(filing.linkToTxt)
            else:
                consume_and_save_xml_form_4_filing(filing.linkToFilingDetails)


begin_date = date(1996, 6, 1)  # inclusive - per SEC api
end_date = date(2021, 6, 1)  # exclusive - per SEC api
download_form_4_filings(begin_date, end_date)
