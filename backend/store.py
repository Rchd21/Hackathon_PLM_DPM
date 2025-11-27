# backend/store.py
from datetime import datetime
from typing import Dict, List, Optional

from .schema import (
    Regulation,
    Requirement,
    RequirementImpact,
    Product,
    HistoryItem,
    CountryCompliance,
    ActionItem,
)


class InMemoryDataStore:
    def __init__(self) -> None:
        # --- Réglementations noyau (Renault) --- #
        self.regulations: Dict[str, Regulation] = {}

        self._init_core_regulations()

        self.requirements: Dict[str, Requirement] = {}
        self.impacts: Dict[str, RequirementImpact] = {}

        self.product = Product(
            id="VEH-EV-01",
            name="Renault EV Platform (exemple)",
            markets=["EU", "UN", "USA"],
            tests=[
                "TEST_DURABILITY_CYCLES",
                "TEST_TRACEABILITY",
                "TEST_CSMS_PROCESS",
                "TEST_SUMS_PROCESS",
                "TEST_CRASH_ISOLATION",
            ],
        )

        self.history: List[HistoryItem] = []

    def _init_core_regulations(self) -> None:
        # EU règlement batterie
        self.regulations["EU-2023-1542"] = Regulation(
            id="EU-2023-1542",
            country="EU",
            title="Règlement (UE) 2023/1542 sur les batteries",
            version="1.0",
            date=datetime(2023, 7, 12),
            text=(
                "Le règlement (UE) 2023/1542 fixe des exigences de durabilité, "
                "de sécurité et de traçabilité pour les batteries de traction des véhicules électriques."
            ),
            url="https://eur-lex.europa.eu/",
            source="core",
        )

        # UN R155
        self.regulations["UN-R155"] = Regulation(
            id="UN-R155",
            country="UN",
            title="UN R155 – Cybersecurity and Cybersecurity Management System",
            version="1.0",
            date=datetime(2021, 3, 1),
            text=(
                "UN R155 impose la mise en place d'un Cybersecurity Management System (CSMS) "
                "couvrant l’identification des menaces, la gestion des risques et la surveillance des incidents "
                "pour les véhicules, durant tout le cycle de vie."
            ),
            url="https://unece.org/",
            source="core",
        )

        # UN R156
        self.regulations["UN-R156"] = Regulation(
            id="UN-R156",
            country="UN",
            title="UN R156 – Software Update and Software Update Management System",
            version="1.0",
            date=datetime(2021, 3, 1),
            text=(
                "UN R156 impose la mise en place d’un Software Update Management System (SUMS) "
                "assurant la maîtrise, la traçabilité et la sécurité de toutes les mises à jour logicielles, "
                "y compris OTA."
            ),
            url="https://unece.org/",
            source="core",
        )

        # FMVSS 305 (USA)
        self.regulations["US-FMVSS-305"] = Regulation(
            id="US-FMVSS-305",
            country="USA",
            title="FMVSS 305 – Electric-powered vehicles: electrical shock protection",
            version="1.0",
            date=datetime(2011, 12, 1),
            text=(
                "La FMVSS 305 fixe des exigences de protection contre le choc électrique et les fuites "
                "d’électrolyte après un crash pour les véhicules électriques."
            ),
            url="https://www.nhtsa.gov/",
            source="core",
        )

    # ---------- Regulations ---------- #
    def list_regulations(self) -> List[Regulation]:
        return sorted(self.regulations.values(), key=lambda r: r.date)

    def add_regulations(self, regs: List[Regulation]) -> None:
        for r in regs:
            self.regulations[r.id] = r

    def get_regulation(self, reg_id: str) -> Optional[Regulation]:
        return self.regulations.get(reg_id)

    # ---------- Requirements ---------- #
    def add_requirements(self, reqs: List[Requirement]) -> None:
        for r in reqs:
            self.requirements[r.id] = r
            self.history.append(
                HistoryItem(
                    requirement_id=r.id,
                    version=1,
                    change_type="created",
                    diff_summary=f"Extraction initiale depuis {r.regulation_id}",
                    timestamp=datetime.utcnow(),
                )
            )

    def list_requirements(self) -> List[Requirement]:
        return sorted(self.requirements.values(), key=lambda r: r.created_at)

    def get_requirements_by_reg(self, reg_id: str) -> List[Requirement]:
        return [r for r in self.requirements.values() if r.regulation_id == reg_id]

    # ---------- Impact ---------- #
    def save_impact(self, impact: RequirementImpact) -> None:
        self.impacts[impact.requirement_id] = impact

    def get_impact(self, req_id: str) -> Optional[RequirementImpact]:
        return self.impacts.get(req_id)

    # ---------- Historique ---------- #
    def get_history(self) -> List[HistoryItem]:
        return sorted(self.history, key=lambda h: h.timestamp)

    # ---------- Compliance ---------- #
    def compute_compliance_by_country(self) -> List[CountryCompliance]:
        countries = sorted({r.country for r in self.requirements.values()})
        res: List[CountryCompliance] = []

        for c in countries:
            reqs = [r for r in self.requirements.values() if r.country == c]
            if not reqs:
                continue
            total = len(reqs)
            covered = sum(1 for r in reqs if r.id in self.impacts and self.impacts[r.id].tests)
            compliance = round(100.0 * covered / total, 1)

            if compliance < 60:
                risk = "Élevé"
            elif compliance < 85:
                risk = "Moyen"
            else:
                risk = "Faible"

            res.append(
                CountryCompliance(
                    country=c,
                    total=total,
                    covered=covered,
                    compliance=compliance,
                    risk=risk,
                )
            )

        return res

    def build_actions_for_country(self, country: str) -> List[ActionItem]:
        actions: List[ActionItem] = []
        reqs = [r for r in self.requirements.values() if r.country == country]
        for r in reqs:
            impact = self.impacts.get(r.id)
            if not impact or not impact.tests:
                actions.append(
                    ActionItem(
                        requirement_id=r.id,
                        country=country,
                        action=(
                            "Compléter l'analyse d'impact, définir les composants et tests "
                            "assurant la conformité à cette exigence."
                        ),
                        components=", ".join(impact.components) if impact else "",
                        tests=", ".join(impact.tests) if impact else "",
                    )
                )
        return actions


# Singleton global pour l’app
STORE = InMemoryDataStore()
