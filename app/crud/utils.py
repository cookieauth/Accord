# app/crud/utils.py

from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResult(BaseModel, Generic[T]):
    total: int
    items: list[T]

    class Config:
        orm_mode = True
