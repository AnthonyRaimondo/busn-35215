from typing import List

from pydantic import BaseModel

from domain.dataFile import DataFile
from domain.documentFormatFile import DocumentFormatFile
from domain.entity import Entity


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
    documentFormatFiles: List[DocumentFormatFile]
    dataFiles: List[DataFile]
    seriesAndClassesContractsInformation: List[]
