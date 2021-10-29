from pydantic import BaseModel


class DocumentFormatFile(BaseModel):
    sequence: str
    description: str
    documentUrl: str
    type: str
    size: str
