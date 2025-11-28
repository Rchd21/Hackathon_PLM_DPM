from datetime import datetime
from typing import Dict, List, Optional

from models import Regulation, Requirement, RequirementImpact, RequirementHistoryItem

R67_TEXT_PATH = "r67_full.txt"


class InMemoryStore:
    def __init__(self) -> None:
        self.regulations: Dict[str, Regulation] = {}
        self.requirements: Dict[str, Requirement] = {}
        self.impacts: Dict[str, RequirementImpact] = {}
        self.history: List[RequirementHistoryItem] = []

        self._load_r67_from_file()

    def _load_r67_from_file(self) -> None:
        try:
            with open(R67_TEXT_PATH, "r", encoding="utf-8") as f:
                text = f.read().strip()
                print(f"[INFO] R67 text loaded from {R67_TEXT_PATH}")
        except FileNotFoundError:
            text = "UNECE R67 text could not be found."

        r67 = Regulation(
            id="UNECE-R67",
            country="UNECE",
            title="UNECE R67 – LPG Vehicle Equipment",
            version="1.0",
            date=datetime(2008, 2, 21),
            url="https://unece.org/transport/vehicle-regulations",
            text=text,
        )

        self.regulations[r67.id] = r67

    # --- Regulations ---
    def get_r67(self) -> Regulation:
        return self.regulations["UNECE-R67"]

    # --- Requirements ---
    def add_requirements(self, reqs: List[Requirement]) -> None:
        for r in reqs:
            self.requirements[r.id] = r
            self.history.append(
                RequirementHistoryItem(
                    timestamp=datetime.utcnow(),
                    requirement_id=r.id,
                    version=r.version,
                    change_type="created",
                    diff_summary="Automatically created",
                )
            )

    def list_requirements(self) -> List[Requirement]:
        return sorted(self.requirements.values(), key=lambda r: r.created_at)

    def get_requirements_for_regulation(self, reg_id: str) -> List[Requirement]:
        return [r for r in self.requirements.values() if r.regulation_id == reg_id]

    # --- Impact ---
    def save_impact(self, impact: RequirementImpact) -> None:
        self.impacts[impact.requirement_id] = impact

    def get_impact(self, req_id: str) -> Optional[RequirementImpact]:
        return self.impacts.get(req_id)

    # --- Compliance update ---
    def update_compliance(self, req_id: str, eu, india, japan):
        req = self.requirements.get(req_id)
        if not req:
            return

        req.compliance_eu = eu
        req.compliance_india = india
        req.compliance_japan = japan

        self.history.append(
            RequirementHistoryItem(
                timestamp=datetime.utcnow(),
                requirement_id=req_id,
                version=req.version,
                change_type="updated",
                diff_summary=f"Compliance updated: EU={eu}, IN={india}, JP={japan}",
            )
        )

    # --- History ---
    def list_history(self) -> List[RequirementHistoryItem]:
        return sorted(self.history, key=lambda h: h.timestamp)


store = InMemoryStore()