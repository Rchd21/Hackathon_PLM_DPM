from datetime import datetime
from typing import List, Dict
from backend.models import Regulation, Product, ProductComponent, TestCase, RequirementImpact

# --- Sample regulations (including versioning) --- #

def get_sample_regulations() -> List[Regulation]:
    return [
        Regulation(
            id="EU-BATT-2025-V1",
            title="Directive Batterie 2025 - Version 1",
            country="EU",
            version="1.0",
            date=datetime(2025, 1, 15),
            url="https://example.org/eu-batt-2025-v1",
            text=(
                "Les batteries des véhicules électriques doivent résister à 60°C "
                "pendant 30 minutes sans fuite ni incendie. "
                "Les constructeurs doivent fournir un rapport de test thermique "
                "pour chaque type de batterie."
            ),
            previous_version_id=None
        ),
        Regulation(
            id="EU-BATT-2025-V2",
            title="Directive Batterie 2025 - Version 2",
            country="EU",
            version="1.1",
            date=datetime(2025, 9, 1),
            url="https://example.org/eu-batt-2025-v2",
            text=(
                "Les batteries des véhicules électriques doivent résister à 70°C "
                "pendant 30 minutes sans fuite ni incendie. "
                "Les constructeurs doivent fournir un rapport de test thermique "
                "pour chaque type de batterie et répéter le test tous les 2 ans."
            ),
            previous_version_id="EU-BATT-2025-V1"
        ),
        Regulation(
            id="US-NHTSA-AIRBAG-2025-V1",
            title="NHTSA Airbag Safety Rule 2025",
            country="USA",
            version="1.0",
            date=datetime(2025, 3, 10),
            url="https://example.org/us-nhtsa-airbag-2025-v1",
            text=(
                "The airbag system must deploy within 30 milliseconds in frontal collisions. "
                "Manufacturers shall provide a validation report with at least 20 crash tests."
            ),
            previous_version_id=None
        )
    ]


# --- Sample product, components & tests --- #

def get_sample_components() -> List[ProductComponent]:
    return [
        ProductComponent(
            id="BATTERY_PACK_V2",
            name="Battery Pack V2",
            description="Pack batterie haute tension 400V"
        ),
        ProductComponent(
            id="AIRBAG_FRONT_V1",
            name="Airbag Frontal V1",
            description="Airbag frontal conducteur"
        )
    ]


def get_sample_tests() -> List[TestCase]:
    return [
        TestCase(
            id="THERMO_60C",
            name="Test thermique 60°C",
            description="Exposition batterie 60°C pendant 30 minutes",
            component_id="BATTERY_PACK_V2"
        ),
        TestCase(
            id="THERMO_70C",
            name="Test thermique 70°C",
            description="Exposition batterie 70°C pendant 30 minutes",
            component_id="BATTERY_PACK_V2"
        ),
        TestCase(
            id="CRASH_30MS",
            name="Crash frontal 30ms",
            description="Test déploiement airbag en 30ms",
            component_id="AIRBAG_FRONT_V1"
        )
    ]


def get_sample_product() -> Product:
    return Product(
        id="EV-CAR-01",
        name="Dacia Zento EV (prototype)",
        markets=["EU", "USA"],
        components=["BATTERY_PACK_V2", "AIRBAG_FRONT_V1"],
        tests=["THERMO_60C", "CRASH_30MS"],
        metadata={"segment": "EV", "platform": "CMF-EV"}
    )


def get_sample_impacts() -> Dict[str, RequirementImpact]:
    """
    Mapping requirement_id -> impact.
    Requirement IDs will be created at runtime, but this gives a template.
    In the real app we will create RequirementImpact dynamically.
    """
    return {}