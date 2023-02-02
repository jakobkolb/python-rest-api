from typing import TypedDict, List
from fastapi import APIRouter
from pydantic import BaseModel


class Route(TypedDict):
    router: APIRouter
    prefix: str
    tags: List[str]


class Example(BaseModel):
    col1: int
    col2: str
    col3: str
