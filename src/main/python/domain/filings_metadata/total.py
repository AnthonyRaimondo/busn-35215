from pydantic import BaseModel


class Total(BaseModel):
    value: int
    relation: str
