from pydantic import BaseModel


class Entity(BaseModel):
    companyName: str
    cik: str
    irsNo: str
    stateOfIncorporation: str
    fiscalYearEnd: str
    sic: str
    type: str
    act: str
    fileNo: str
    filmNo: str
