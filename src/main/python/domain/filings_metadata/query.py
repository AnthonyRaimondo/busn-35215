from pydantic import BaseModel


class Query(BaseModel):
    from_: int
    size: int

    class Config:
        fields = {
            'from_': 'from'
        }
