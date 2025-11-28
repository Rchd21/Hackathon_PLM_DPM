from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


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
    version: str
    text_raw: str
    text_engineering: str
    created_at: datetime = field(default_factory=datetime.utcnow)

    # NEW — Compliance fields
    compliance_eu: Optional[str] = None     # OK / NOK / NA
    compliance_india: Optional[str] = None
    compliance_japan: Optional[str] = None


@dataclass
class RequirementImpact:
    requirement_id: str
    components: List[str]
    tests: List[str]
    documents: List[str]
    criticality: str
    validation_actions: List[str]


@dataclass
class RequirementHistoryItem:
    timestamp: datetime
    requirement_id: str
    version: str
    change_type: str    # "created", "updated"
    diff_summary: str