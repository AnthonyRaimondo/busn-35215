from typing import List, Optional

from pydantic import BaseModel

from domain.filings_metadata.dataFile import DataFile
from domain.filings_metadata.documentFormatFile import DocumentFormatFile
from domain.filings_metadata.entity import Entity
from domain.filings_metadata.seriesAndClassesContractsInformation import SeriesAndClassesContractsInformation


class Filing(BaseModel):
    id: str
    accessionNo: str
    cik: str
    ticker: str
    companyName: str
    companyNameLong: str
    formType: str
    description: str
    filedAt: str
    linkToTxt: str
    linkToHtml: str
    linkToXbrl: str
    linkToFilingDetails: str
    entities: List[Entity]
    documentFormatFiles: Optional[List[DocumentFormatFile]]
    dataFiles: Optional[List[DataFile]]
    seriesAndClassesContractsInformation: Optional[List[SeriesAndClassesContractsInformation]]
