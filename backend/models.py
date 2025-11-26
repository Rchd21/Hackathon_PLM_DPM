from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class Regulation(BaseModel):
    id: str
    title: str
    country: str
    version: str
    date: datetime
    url: Optional[str]
    text: str
    previous_version_id: Optional[str] = None

    domain: str = "automotive"
    scope: str = "safety"


class Requirement(BaseModel):
    id: str
    regulation_id: str
    country: str
    version: str
    text_raw: str
    text_engineering: str
    created_at: datetime
    updated_at: datetime


class ProductComponent(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class TestCase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    component_id: str


class RequirementImpact(BaseModel):
    requirement_id: str
    components: List[str]
    tests: List[str]
    documents: List[str]


class RequirementHistoryItem(BaseModel):
    requirement_id: str
    version: str
    timestamp: datetime
    change_type: str  # "created", "updated"
    diff_summary: str


class ComplianceStatus(BaseModel):
    country: str
    product_id: str
    compliance_percent: float
    non_compliant_requirements: List[str]
    risk_level: str  # "Low", "Medium", "High"
    recommended_actions: List[str]


class Product(BaseModel):
    id: str
    name: str
    markets: List[str]  # countries
    components: List[str]  # component ids
    tests: List[str]  # test ids
    domain: str = "automotive"
    metadata: Dict[str, str] = {}