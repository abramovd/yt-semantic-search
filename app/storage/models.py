import numpy as np

from pydantic import BaseModel, Field
from datetime import datetime


class Document(BaseModel):
    id: int | None = None
    title: str
    created_at: datetime
    url: str
    meta: dict = Field(default_factory=dict)


class Chunk(BaseModel):
    id: int | None = None
    chunk_index: int
    start_ts: float
    end_ts: float
    text: str

    document_id: int

    embedding: np.ndarray

    class Config:
        arbitrary_types_allowed = True


class SearchResultChunk(BaseModel):
    id: int | None = None
    chunk_index: int
    start_ts: float
    end_ts: float
    text: str
    distance: float
    document_title: str
    document_url: str
