import json
import requests
from typing import List
from datetime import datetime
from models import Requirement, Regulation

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"


def call_ollama(prompt: str) -> str:
    """Envoi d’un prompt à Ollama (Mistral) via HTTP."""
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }
    response = requests.post(OLLAMA_URL, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"Ollama error: {response.text}")

    data = response.json()
    return data.get("response", "")


def extract_requirements_from_text(regulation: Regulation, start_index: int = 1) -> List[Requirement]:
    """Extraction d’exigences orientées ingénierie système depuis UNECE R67."""

    text = regulation.text
    reg_id = regulation.id
    country = regulation.country

    # --- PROMPT INGÉNIERIE SYSTÈME ---
    prompt = f"""
You are an automotive systems engineer working on regulatory compliance (UNECE R67).

Extract ONLY technical, atomic, verifiable engineering requirements from the regulation text below.

SOURCE TEXT:
\"\"\"{text}\"\"\"

INSTRUCTIONS:
- Identify only real obligations, not definitions or context.
- Each requirement must be:
    * Atomic (one obligation per item)
    * Testable (measurable acceptance criteria)
    * Engineering-style ("The system shall ..." / "The LPG system shall ...")
    * Linked to a system, component, function or constraint
- If a number like "R67-5" is found, reuse it as the requirement ID.
- If no ID exists, generate one using this format:
      "{reg_id}-X"
  where X starts at {start_index}.

OUTPUT FORMAT — STRICT JSON ONLY:
[
  {{
    "id": "R67-5",
    "text_raw": "Exact sentence from regulation...",
    "text_engineering": "The LPG system shall ..."
  }},
  ...
]

Return ONLY valid JSON with a list of objects.
"""

    print("[INFO] Envoi du texte à Mistral via Ollama…")
    raw = call_ollama(prompt)

    # --- PARSING JSON ---
    try:
        data = json.loads(raw)
    except Exception:
        print("[ERREUR] JSON invalide renvoyé par Ollama :")
        print(raw)
        return []

    # --- CONVERT JSON → LISTE DE REQUIREMENT ---
    requirements = []

    for idx, item in enumerate(data, start=start_index):

        # Gestion automatique de l’ID si manquant
        rid = item.get("id")
        if not rid or len(rid.strip()) == 0:
            rid = f"{reg_id}-{idx}"

        requirements.append(
            Requirement(
                id=rid,
                regulation_id=reg_id,
                country=country,
                version="1.0",
                text_raw=item.get("text_raw", "").strip(),
                text_engineering=item.get("text_engineering", "").strip(),
                created_at=datetime.utcnow(),
            )
        )

    return requirements