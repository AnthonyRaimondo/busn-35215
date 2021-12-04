from typing import List, Optional

from pydantic import BaseModel

from domain.filings_metadata.dataFile import DataFile
from domain.filings_metadata.documentFormatFile import DocumentFormatFile
from domain.filings_metadata.entity import Entity
from domain.filings_metadata.seriesAndClassesContractsInformation import SeriesAndClassesContractsInformation


class Filing(BaseModel):
    id: str = None
    accessionNo: str = None
    cik: str = None
    ticker: str = None
    companyName: str = None
    companyNameLong: str = None
    formType: str = None
    description: str = None
    filedAt: str = None
    linkToTxt: str = None
    linkToHtml: str = None
    linkToXbrl: str = None
    linkToFilingDetails: str = None
    entities: List[Entity] = None
    documentFormatFiles: Optional[List[DocumentFormatFile]] = None
    dataFiles: Optional[List[DataFile]] = None
    seriesAndClassesContractsInformation: Optional[List[SeriesAndClassesContractsInformation]] = None
