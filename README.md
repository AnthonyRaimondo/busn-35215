# busn-35215

Possible modifications to payload for retrieving filings from the SEC website:
* Configure the size of the response from the SEC's api by changing the "size" field of SEC_PAYLOAD (consumption_constants.py)
    * Though, the SEC api seems to return no more than 200 filings per request
* Modify begin_date to change the date from which the SEC query begins
* Modify end_date to change the date from which the SEC query ends
* To change the sorting of filings, use sort[0].filedAt.order in SEC_PAYLOAD (consumption_constants.py) - "asc" or "desc"
