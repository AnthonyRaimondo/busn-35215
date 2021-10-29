import json
import os
import urllib.request

from DateTime import DateTime

from constant.consumption_constants import FORM_4_FILTER, API, ENCODING, SEC_PAYLOAD
from domain.sec_response import SECResponse


def construct_payload(begin: DateTime, end: DateTime, filings_filter: str) -> dict:
    SEC_PAYLOAD.get("query").get("query_string")["query"] = filings_filter.format(begin, end)
    return SEC_PAYLOAD


def call_sec_api(request_body: dict) -> SECResponse:
    json_payload = json.dumps(request_body)
    payload_bytes = json_payload.encode(ENCODING)
    request = urllib.request.Request(API)
    request.add_header('Authorization', API_KEY)
    request.add_header('Content-Type', 'application/json; charset=' + ENCODING)
    request.add_header('Content-Length', len(payload_bytes))
    response = urllib.request.urlopen(request, payload_bytes)
    response_body = response.read()
    return json.loads(response_body.decode(ENCODING))


API_KEY: str = os.environ.get("SEC_API_KEY")
begin_date
end_date
payload = construct_payload(begin_date, end_date, FORM_4_FILTER)
sec_response = call_sec_api(payload)
