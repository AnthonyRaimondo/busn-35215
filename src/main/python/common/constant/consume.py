API = "https://api.sec-api.io"
ENCODING = 'utf-8'
FORM_4_FILTER = "formType:\"4\" " \
                "AND formType:(NOT \"N-4\") " \
                "AND formType:(NOT \"F-4\") " \
                "AND formType:(NOT \"S-4\") " \
                "AND formType:(NOT \"4/A\") " \
                "AND filedAt:[{} TO {}]"
SEC_PAYLOAD = {
    "query": {
        "query_string": {
            "query": FORM_4_FILTER
        }
    },
    "from": 0,
    "size": 5,
    "sort": [
        {
            "filedAt": {
                "order": "asc"
            }
        }
    ]
}
SHAREHOLDER_TABLE = "Issuer Name and Ticker or Trading Symbol"
NON_DERIVATIVE_TABLE = "Table I - Non-Derivative Securities"
DERIVATIVE_TABLE = "Table II - Derivative Securities"
NAME_HEADER = "Name and Address of Reporting Person"
CIK = "CIK="
RELATIONSHIP_OF_REPORTING_PERSONS_INDICATOR = "<span class=\"FormData\">X</span>"
ISSUER_NAME_AND_TICKER = "Issuer Name and Ticker or Trading Symbol"
DIRECTOR = "Director"
TEN_PERCENT_OWNER = "10% Owner"
OFFICER = "Officer (give title below)"
OTHER_RELATIONSHIP = "Other (specify below)"
BAD_RESPONSES = [
    "Authorization header is invalid",
    "File Unavailable</title>",
    "File Not Found Error Alert (404)"
]
