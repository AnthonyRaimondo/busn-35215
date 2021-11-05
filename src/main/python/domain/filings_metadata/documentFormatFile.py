from typing import Optional

from pydantic import BaseModel


class DocumentFormatFile(BaseModel):
    sequence: Optional[str] = None
    description: Optional[str] = None
    documentUrl: Optional[str] = None
    type: Optional[str] = None
    size: Optional[str] = None
