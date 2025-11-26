"""
Impact engine : relie exigences -> composants / tests & évalue l'impact
"""

from typing import List
from backend.models import Requirement, RequirementImpact
from backend.data_store import InMemoryDataStore


def infer_impacts_for_requirement(
    requirement: Requirement, store: InMemoryDataStore
) -> RequirementImpact:
    """
    Heuristique très simple basée sur des mots-clés.
    """

    text = requirement.text_engineering.lower()
    components: List[str] = []
    tests: List[str] = []
    documents: List[str] = []

    # Composants
    if "batterie" in text or "battery" in text:
        components.append("BATTERY_PACK_V2")
    if "airbag" in text:
        components.append("AIRBAG_FRONT_V1")

    # Tests (détection très naïve)
    if "60°" in text or "60c" in text:
        tests.append("THERMO_60C")
    if "70°" in text or "70c" in text:
        tests.append("THERMO_70C")
    if "30 milliseconds" in text or "30 millisecondes" in text:
        tests.append("CRASH_30MS")

    # Documents
    if "rapport" in text or "report" in text:
        documents.append("RPT_THERMO_2025")

    # Fallback: si aucune détection, on met composant générique
    if not components:
        components = [c.id for c in store.components.values()]

    impact = RequirementImpact(
        requirement_id=requirement.id,
        components=list(set(components)),
        tests=list(set(tests)),
        documents=list(set(documents)),
    )
    return impact