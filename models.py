# models.py
from dataclasses import dataclass,field
from datetime import datetime
from typing import List


@dataclass
class Regulation:
    id: str
    country: str
    title: str
    version: str
    date: datetime
    url: str
    text: str


@dataclass
class Requirement:
    id: str
    regulation_id: str
    country: str
    version: str ="1.0"
    text_raw: str = ""
    text_engineering: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RequirementImpact:
    requirement_id: str
    components: List[str]
    tests: List[str]
    documents: List[str]
    criticality: str = "medium"
    validation_actions: List[str] = field(default_factory=list) 


@dataclass
class RequirementHistoryItem:
    timestamp: datetime
    requirement_id: str
    version: str
    change_type: str  # "created", "updated"
    diff_summary: str
