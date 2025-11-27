# impact_engine.py
import json
from typing import List

import requests

from models import Requirement, RequirementImpact


# ==========================
#  Config Ollama / Mistral
# ==========================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"  # ou "mistral:7b" selon ce que tu as pull


# =========
#  Fallback
# =========

COMPONENT_KEYWORDS = {
    "tank": ["LPG_TANK"],
    "cylinder": ["LPG_TANK"],
    "container": ["LPG_TANK"],

    "valve": ["LPG_VALVE"],
    "multivalve": ["LPG_MULTIVALVE"],
    "safety valve": ["LPG_SAFETY_VALVE"],
    "shut-off valve": ["LPG_SHUTOFF_VALVE"],

    "pipe": ["LPG_PIPE"],
    "piping": ["LPG_PIPE"],
    "hose": ["LPG_HOSE"],
    "tube": ["LPG_PIPE"],

    "filter": ["LPG_FILTER"],
    "regulator": ["LPG_PRESSURE_REGULATOR"],
    "pressure regulator": ["LPG_PRESSURE_REGULATOR"],

    "sensor": ["LPG_SENSOR"],
    "temperature sensor": ["LPG_TEMP_SENSOR"],
    "pressure sensor": ["LPG_PRESSURE_SENSOR"],
    "level sensor": ["LPG_LEVEL_SENSOR"],

    "fuel pump": ["LPG_PUMP"],
    "pump": ["LPG_PUMP"],

    "ecu": ["LPG_ECU"],
    "control unit": ["LPG_ECU"],
    "controller": ["LPG_ECU"],

    "electrical": ["LPG_ELECTRICAL_SYSTEM"],
    "wiring": ["LPG_ELECTRICAL_SYSTEM"],
    "connector": ["LPG_CONNECTOR"],
    "cable": ["LPG_ELECTRICAL_SYSTEM"],

    "system": ["LPG_SYSTEM"],
}

TEST_KEYWORDS = {
    "pressure": ["TEST_PRESSURE"],
    "leak": ["TEST_LEAK"],
    "leakage": ["TEST_LEAK"],
    "fire": ["TEST_FIRE"],
    "crash": ["TEST_CRASH"],
    "impact": ["TEST_IMPACT"],
    "drop": ["TEST_DROP"],
    "temperature": ["TEST_THERMAL"],
    "durability": ["TEST_DURABILITY"],
}

DOC_KEYWORDS = {
    "documentation": ["DOC_SYSTEM_SPEC"],
    "manual": ["DOC_USER_MANUAL"],
    "installation": ["DOC_INSTALLATION_GUIDE"],
    "certificate": ["DOC_CONFORMITY_REPORT"],
    "conformity": ["DOC_CONFORMITY_REPORT"],
    "marking": ["DOC_LABELING"],
    "label": ["DOC_LABELING"],
}


# =====================
#  Petites fonctions
# =====================

def _infer_criticality(text: str) -> str:
    """
    Détermine une criticité simple à partir de mots-clés.
    """
    t = text.lower()

    safety_words = ["leak", "leakage", "fire", "explosion", "crash", "safety", "hazard"]
    if any(w in t for w in safety_words):
        return "HIGH"

    perf_words = ["pressure", "temperature", "durability", "fatigue"]
    if any(w in t for w in perf_words):
        return "MEDIUM"

    doc_words = ["documentation", "manual", "marking", "label", "labeling"]
    if any(w in t for w in doc_words):
        return "LOW"

    return "MEDIUM"


def _build_validation_actions(components: List[str], tests: List[str], criticality: str) -> List[str]:
    """
    Génère des actions V&V lisibles pour un ingénieur.
    """
    actions: List[str] = []

    if tests:
        actions.append(
            f"Planifier et exécuter les essais suivants : {', '.join(tests)}."
        )

    if components:
        actions.append(
            f"Revoir la conception et la conformité des composants : {', '.join(components)}."
        )

    if criticality == "HIGH":
        actions.append(
            "Prévoir une analyse de sécurité (FTA/FMEA) et une revue avec l’équipe sécurité véhicule."
        )
    elif criticality == "MEDIUM":
        actions.append(
            "Tracer la couverture de cette exigence dans la matrice exigences ↔ tests."
        )
    else:
        actions.append(
            "Vérifier la mise à jour de la documentation associée."
        )

    return actions


# ============================
#  Appel Ollama / Mistral
# ============================

def _call_ollama_for_impact(prompt: str) -> dict:
    """
    Appelle Mistral via Ollama pour analyser l'impact d'une exigence.

    On attend un JSON du type :
    {
      "components": [...],
      "tests": [...],
      "documents": [...],
      "criticality": "HIGH|MEDIUM|LOW",
      "validation_actions": [...]
    }
    """
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=120)
    except Exception as e:
        print("[Ollama] Erreur de connexion :", e)
        return {}

    if resp.status_code != 200:
        print("[Ollama] Code HTTP inattendu :", resp.status_code)
        print(resp.text)
        return {}

    data = resp.json()
    raw_text = data.get("response", "")

    # Essayer d’isoler le JSON (au cas où Mistral parle autour)
    try:
        start = raw_text.index("{")
        end = raw_text.rindex("}") + 1
        json_str = raw_text[start:end]
    except ValueError:
        print("[Ollama] Impossible de trouver un bloc JSON dans la réponse :")
        print(raw_text)
        return {}

    try:
        return json.loads(json_str)
    except Exception as e:
        print("[Ollama] JSON invalide :", e)
        print(json_str)
        return {}


# ============================
#  Fonction principale
# ============================

def infer_impact_for_requirement(req: Requirement) -> RequirementImpact:
    """
    Déduit l’impact d’une exigence R67 en combinant :
    - ce que propose Mistral (Ollama)
    - un fallback simple à base de mots-clés
    """
    base_text = req.text_engineering or req.text_raw or ""
    text_lower = base_text.lower()

    # -------- 1) Demander une analyse à Mistral -------- #
    prompt = f"""
You are a systems engineer for an automotive OEM (Renault).
You must analyse one regulatory requirement from UNECE R67 and map it to
vehicle architecture and verification activities.

Requirement (raw + engineering form):

RAW:
\"\"\"{req.text_raw}\"\"\"

ENGINEERING:
\"\"\"{req.text_engineering}\"\"\"

Return ONLY ONE JSON object with the structure:

{{
  "components": ["LPG_TANK", "LPG_VALVE", ...],   // short component ids
  "tests": ["TEST_PRESSURE", "TEST_LEAK", ...],   // short test ids
  "documents": ["DOC_R67_COMPLIANCE", ...],       // short doc ids
  "criticality": "HIGH" | "MEDIUM" | "LOW",
  "validation_actions": [
      "Sentence 1 describing what validation must be done.",
      "Sentence 2 ..."
  ]
}}

Rules:
- Use HIGH criticality for safety-related requirements (fire, leakage, crash, explosion...).
- Use MEDIUM for performance / robustness requirements (pressure, temperature, durability...).
- Use LOW for documentation / labeling / traceability only.
- Always return valid JSON, no explanation outside the JSON.
"""
    print(f"[IMPACT] Appel Mistral/Ollama pour l'exigence {req.id}...")
    llm_result = _call_ollama_for_impact(prompt)

    components: List[str] = []
    tests: List[str] = []
    documents: List[str] = []
    criticality: str = ""
    validation_actions: List[str] = []

    if llm_result:
        components = llm_result.get("components") or []
        tests = llm_result.get("tests") or []
        documents = llm_result.get("documents") or []
        criticality = llm_result.get("criticality") or ""
        validation_actions = llm_result.get("validation_actions") or []

    # -------- 2) Fallback dictionnaire si c'est vide / incomplet -------- #

    # Composants via mots-clés
    for kw, comps in COMPONENT_KEYWORDS.items():
        if kw in text_lower:
            for c in comps:
                if c not in components:
                    components.append(c)

    # Tests via mots-clés
    for kw, ts in TEST_KEYWORDS.items():
        if kw in text_lower:
            for t in ts:
                if t not in tests:
                    tests.append(t)

    # Documents via mots-clés
    for kw, docs in DOC_KEYWORDS.items():
        if kw in text_lower:
            for d in docs:
                if d not in documents:
                    documents.append(d)

    # Si vraiment aucun composant détecté mais qu'on parle du système
    if not components and ("system" in text_lower or "vehicle" in text_lower):
        components.append("UNSPECIFIED_COMPONENT")

    # Criticité si absente
    if not criticality:
        criticality = _infer_criticality(text_lower)

    # Actions de validation si absentes
    if not validation_actions:
        validation_actions = _build_validation_actions(components, tests, criticality)

    # -------- 3) Construction de l'objet RequirementImpact -------- #
    return RequirementImpact(
        requirement_id=req.id,
        components=components,
        tests=tests,
        documents=documents,
        criticality=criticality,
        validation_actions=validation_actions,
    )