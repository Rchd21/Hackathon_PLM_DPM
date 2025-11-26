from typing import Dict, List, Optional
from datetime import datetime

# Imports internes au package backend
from .models import (
    Regulation,
    Requirement,
    Product,
    ProductComponent,
    TestCase,
    RequirementImpact,
    RequirementHistoryItem,
)
from .sample_data import (
    get_sample_regulations,
    get_sample_components,
    get_sample_product,
    get_sample_tests,
)
from .versioning import create_history_item

# Imports des sources réelles (si tu as créé ces fichiers)
from .sources.eurlex_client import get_eu_regulation
from .sources.federalregister_client import search_us_regulations


class InMemoryDataStore:
    """
    Très simple 'base de données' en mémoire pour la démo hackathon.
    """

    def __init__(self):
        # Données d'exemple chargées au démarrage
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

    # --- Regulations (interne) --- #

    def list_regulations(self) -> List[Regulation]:
        return sorted(self.regulations.values(), key=lambda r: r.date)

    def get_regulation(self, reg_id: str) -> Optional[Regulation]:
        return self.regulations.get(reg_id)

    # --- Import depuis des sources réelles --- #

    def import_eu_regulation(self, celex_id: str) -> Regulation:
        """
        Importe une réglementation UE depuis EUR-Lex/Cellar via son CELEX ID.
        Nécessite que backend/sources/eurlex_client.py soit configuré.
        """
        reg = get_eu_regulation(celex_id)
        self.regulations[reg.id] = reg
        return reg

    def import_us_regulations_by_topic(
        self, topic: str, limit: int = 5
    ) -> List[Regulation]:
        """
        Importe des réglementations US depuis le Federal Register,
        filtrées par mot-clé (topic).
        """
        regs = search_us_regulations(topic, limit)
        for reg in regs:
            self.regulations[reg.id] = reg
        return regs

    # --- Requirements --- #

    def add_requirements(self, reqs: List[Requirement]):
        for r in reqs:
            self.requirements[r.id] = r
            self.history.append(
                create_history_item(
                    requirement=r,
                    change_type="created",
                    diff_summary="Initial extraction",
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

        non_compliant: List[str] = []

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
    
    def import_worldwide_by_topic(self, topic: str, us_limit: int = 5) -> None:
        """
        Exemple simple : on importe des textes pour plusieurs juridictions
        autour d'un même sujet (ex: 'battery', 'airbag', 'cybersecurity').

        Pour l'instant :
        - USA : Federal Register par mot-clé
        - EU : à toi de choisir les CELEX pertinents que tu veux surveiller
        """
        # 1) USA : Federal Register
        us_regs = self.import_us_regulations_by_topic(topic, limit=us_limit)

        # 2) EU : ici on peut faire une petite table de correspondance
        #    sujet -> liste de CELEX à surveiller
        topic_map = {
            "battery": ["32023R1542"],
            "batterie": ["32023R1542"],
            "airbag": [],  # à remplir si tu trouves des CELEX spécifiques
        }
        celex_list = topic_map.get(topic.lower(), [])

        eu_regs = []
        for celex in celex_list:
            try:
                reg = self.import_eu_regulation(celex)
                eu_regs.append(reg)
            except Exception:
                # on ignore les erreurs pour la démo
                continue

        # Tu pourrais ajouter ici d'autres sources (FR / JP / etc.)
        # en appelant d'autres clients quand tu les auras créés.

        return {
            "US": us_regs,
            "EU": eu_regs,
        }
