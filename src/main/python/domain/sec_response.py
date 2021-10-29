from typing import List

from pydantic import BaseModel

from domain.filing import Filing
from domain.query import Query
from domain.total import Total


class SECResponse(BaseModel):
    total: Total
    query: Query
    filings: List[Filing]
