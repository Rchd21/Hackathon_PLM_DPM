# backend/schemas.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Regulation(BaseModel):
    id: str
    country: str
    title: str
    version: str
    date: datetime
    text: str
    url: Optional[str] = None
    source: str = "internal"


class Requirement(BaseModel):
    id: str
    regulation_id: str
    country: str
    version: str
    text_raw: str
    text_engineering: str
    created_at: datetime


class RequirementImpact(BaseModel):
    requirement_id: str
    components: List[str]
    tests: List[str]
    documents: List[str]


class Product(BaseModel):
    id: str
    name: str
    markets: List[str]
    tests: List[str]


class HistoryItem(BaseModel):
    requirement_id: str
    version: int
    change_type: str
    diff_summary: str
    timestamp: datetime


class CountryCompliance(BaseModel):
    country: str
    total: int
    covered: int
    compliance: float
    risk: str


class ActionItem(BaseModel):
    requirement_id: str
    country: str
    action: str
    components: str
    tests: str
