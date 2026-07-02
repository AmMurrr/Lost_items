from datetime import date

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    description: str = Field(..., min_length=1)
    station: str = Field(..., min_length=1)
    loss_date: date


class SearchResult(BaseModel):
    id: int
    description: str
    station: str
    found_date: date
    similarity: float
