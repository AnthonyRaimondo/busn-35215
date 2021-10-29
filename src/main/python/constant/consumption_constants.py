API = "https://api.sec-api.io"
FORM_4_FILTER = "formType:\"4\" AND formType:(NOT \"N-4\") AND formType:(NOT \"4/A\") AND filedAt:[{}} TO {}}]"
ENCODING = 'utf-8'
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
                "order": "desc"
            }
        }
    ]
}
