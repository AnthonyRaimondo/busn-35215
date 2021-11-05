from typing import Optional

from pydantic import BaseModel


class Entity(BaseModel):
    companyName: Optional[str] = None
    cik: Optional[str] = None
    irsNo: Optional[str] = None
    stateOfIncorporation: Optional[str] = None
    fiscalYearEnd: Optional[str] = None
    sic: Optional[str] = None
    type: Optional[str] = None
    act: Optional[str] = None
    fileNo: Optional[str] = None
    filmNo: Optional[str] = None
