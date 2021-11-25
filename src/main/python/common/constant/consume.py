API = "https://api.sec-api.io"
ARCHIVE_API = "https://archive.sec-api.io"
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
NON_DERIVATIVE_TABLE_TXT = "Non-Derivative Securities Acquired"
DERIVATIVE_TABLE = "Table II - Derivative Securities"
DERIVATIVE_TABLE_TXT = "Derivative Securities Acquired"
NAME_HEADER = "Name and Address of Reporting Person"
CIK = "CIK="
RELATIONSHIP_OF_REPORTING_PERSONS_INDICATOR = "<span class=\"FormData\">X</span>"
ISSUER_NAME_AND_TICKER = "Issuer Name and Ticker or Trading Symbol"
IRS_SSN = "IRS or Social Security Number of Reporting Person"
DIRECTOR = "Director"
TEN_PERCENT_OWNER = "10% Owner"
OFFICER = "Officer (give title below)"
OFFICER_WITH_NEWLINE = "Officer\n"
OTHER_RELATIONSHIP = "Other (specify below)"
OTHER_RELATIONSHIP_WITH_NEWLINE = "Other\n"
RELATIONSHIP_HEADER = "Relationship of Reporting Person"
BAD_RESPONSES = [
    "Authorization header is invalid",
    "File Unavailable</title>",
    "File Not Found Error Alert (404)"
    "Issuer Name and Ticker orTrading Symbol"
]
SPECIAL_CHARS = {" ", "."}
COMPANY_INFO_SECTION_TXT_FILE = "SUBJECT COMPANY:"
REPORTING_OWNER_SECTION_TXT_FILE = "REPORTING-OWNER"
CIK_IDENTIFIER = "CENTRAL INDEX KEY:"
CONFORMED_NAME = "CONFORMED NAME:"
INDIVIDUAL_OR_JOINT_FILING = "Individual or Joint/Group Filing"
RELATIONSHIP_OPTIONS = [
    OFFICER_WITH_NEWLINE,
    OFFICER,
    OTHER_RELATIONSHIP,
    OTHER_RELATIONSHIP_WITH_NEWLINE,
    TEN_PERCENT_OWNER,
    DIRECTOR
]
