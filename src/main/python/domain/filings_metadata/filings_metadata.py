from typing import List

from pydantic import BaseModel

from domain.filings_metadata.filing import Filing
from domain.filings_metadata.query import Query
from domain.filings_metadata.total import Total


class FilingsMetadata(BaseModel):
    total: Total
    query: Query
    filings: List[Filing]
