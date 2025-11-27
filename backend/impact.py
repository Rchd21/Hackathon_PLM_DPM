# backend/impact.py
from .schema import RequirementImpact, Requirement
from .store import STORE


def infer_impact(req: Requirement) -> RequirementImpact:
    """
    Heuristique simplifiée basée sur des mots-clés auto :
    - batterie / battery  -> BAT_PACK, BMS, tests durabilité & traçabilité
    - cyber / CSMS       -> TCU, tests CSMS
    - software / update  -> TCU, UPDATE_SERVER, tests SUMS
    - crash / HV         -> BAT_PACK, HV_DISCONNECT, test crash isolation
    """
    text = (req.text_raw + " " + req.text_engineering).lower()

    components = set()
    tests = set()
    docs = set()

    if "batterie" in text or "battery" in text:
        components.update(["BAT_PACK", "BMS"])
        tests.add("TEST_DURABILITY_CYCLES")
        docs.add("SPEC_BATTERY_DURABILITY")

    if "traçabil" in text or "traceab" in text:
        components.add("BAT_PACK")
        tests.add("TEST_TRACEABILITY")
        docs.add("SPEC_BATTERY_PASSPORT")

    if "cyber" in text or "csms" in text:
        components.add("TCU")
        tests.add("TEST_CSMS_PROCESS")
        docs.add("CYBERSECURITY_PLAN")

    if "software" in text or "update" in text or "ota" in text or "sums" in text:
        components.update(["TCU", "UPDATE_SERVER"])
        tests.add("TEST_SUMS_PROCESS")
        docs.add("SUMS_PLAN")

    if "crash" in text or "choc électrique" in text or "hv" in text:
        components.update(["BAT_PACK", "HV_DISCONNECT"])
        tests.add("TEST_CRASH_ISOLATION")
        docs.add("SPEC_HV_ISOLATION")

    return RequirementImpact(
        requirement_id=req.id,
        components=list(components),
        tests=list(tests),
        documents=list(docs),
    )
