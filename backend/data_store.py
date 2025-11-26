from typing import Dict, List, Optional
from datetime import datetime

from backend.models import (
    Regulation,
    Requirement,
    Product,
    ProductComponent,
    TestCase,
    RequirementImpact,
    RequirementHistoryItem,
)
from backend.sample_data import (
    get_sample_regulations,
    get_sample_components,
    get_sample_product,
    get_sample_tests,
)
from backend.versioning import create_history_item


class InMemoryDataStore:
    """
    Très simple 'base de données' en mémoire pour la démo hackathon.
    """

    def __init__(self):
        
        self.regulations: Dict[str, Regulation] = {
            r.id: r for r in get_sample_regulations()
        }
        self.requirements: Dict[str, Requirement] = {}
        self.components: Dict[str, ProductComponent] = {
            c.id: c for c in get_sample_components()
        }
        self.tests: Dict[str, TestCase] = {t.id: t for t in get_sample_tests()}
        self.product: Product = get_sample_product()

        self.impacts: Dict[str, RequirementImpact] = {}
        self.history: List[RequirementHistoryItem] = []

    # --- Regulations --- #

    def list_regulations(self) -> List[Regulation]:
        return sorted(self.regulations.values(), key=lambda r: r.date)

    def get_regulation(self, reg_id: str) -> Optional[Regulation]:
        return self.regulations.get(reg_id)

    # --- Requirements --- #

    def add_requirements(self, reqs: List[Requirement]):
        for r in reqs:
            self.requirements[r.id] = r
            self.history.append(
                create_history_item(
                    requirement=r, change_type="created", diff_summary="Initial extraction"
                )
            )

    def update_requirement(self, requirement: Requirement, diff_summary: str):
        self.requirements[requirement.id] = requirement
        self.history.append(
            create_history_item(
                requirement=requirement,
                change_type="updated",
                diff_summary=diff_summary,
            )
        )

    def list_requirements(self) -> List[Requirement]:
        return sorted(self.requirements.values(), key=lambda r: r.created_at)

    def get_requirements_by_reg(self, reg_id: str) -> List[Requirement]:
        return [r for r in self.requirements.values() if r.regulation_id == reg_id]

    # --- Impacts --- #

    def save_impact(self, impact: RequirementImpact):
        self.impacts[impact.requirement_id] = impact

    def get_impact(self, requirement_id: str) -> Optional[RequirementImpact]:
        return self.impacts.get(requirement_id)

    # --- History --- #

    def get_history(self) -> List[RequirementHistoryItem]:
        return sorted(self.history, key=lambda h: h.timestamp)

    # --- Simple compliance computation --- #

    def compute_compliance_for_country(self, country: str):
        """
        Très simplifié : si une exigence liée à un test non présent dans le produit -> non conforme.
        """
        relevant_reqs = [
            r for r in self.requirements.values() if r.country == country
        ]
        if not relevant_reqs:
            return 100.0, []

        non_compliant = []
        for r in relevant_reqs:
            impact = self.impacts.get(r.id)
            if not impact:
                non_compliant.append(r.id)
                continue

            # Si au moins un test requis n'est pas dans le produit, non conforme
            for test_id in impact.tests:
                if test_id not in self.product.tests:
                    non_compliant.append(r.id)
                    break

        compliance_percent = 100.0 * (
            1.0 - len(non_compliant) / max(1, len(relevant_reqs))
        )
        return round(compliance_percent, 1), non_compliant