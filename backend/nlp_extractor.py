"""
Module NLP ultra simplifié pour le hackathon.

Objectif : extraire des phrases "exigences" à partir d'un texte réglementaire
et les reformuler en langage ingénierie.
"""

from typing import List
from datetime import datetime
from backend.models import Regulation, Requirement


def split_sentences(text: str) -> List[str]:
    # découpe ultra simple pour la démo
    raw_sentences = text.replace("?", ".").replace("!", ".").split(".")
    sentences = [s.strip() for s in raw_sentences if s.strip()]
    return sentences


def is_requirement_sentence(sentence: str) -> bool:
    keywords = [
        "doit",
        "doivent",
        "shall",
        "must",
        "obligatoire",
        "shall provide",
        "doivent fournir",
    ]
    s_lower = sentence.lower()
    return any(k in s_lower for k in keywords)


def to_engineering_text(sentence: str) -> str:
    """
    Reformulation très simple : enlève un peu le juridique et garde le concret.
    Dans un vrai projet on utiliserait un modèle LLM.
    """
    s = sentence.strip()
    # mini heuristique
    s = s.replace("Les constructeurs doivent", "L'ingénieur produit doit")
    s = s.replace("Manufacturers shall", "Engineering team shall")
    s = s.replace("must", "doit")
    s = s.replace("shall", "doit")
    return s


def extract_requirements_from_regulation(
    regulation: Regulation, start_index: int = 1
) -> List[Requirement]:
    sentences = split_sentences(regulation.text)
    requirements: List[Requirement] = []
    counter = start_index
    now = datetime.utcnow()

    for sent in sentences:
        if not is_requirement_sentence(sent):
            continue

        req = Requirement(
            id=f"REQ_{regulation.country}_{counter:04d}",
            regulation_id=regulation.id,
            country=regulation.country,
            version=regulation.version,
            text_raw=sent,
            text_engineering=to_engineering_text(sent),
            created_at=now,
            updated_at=now,
        )
        requirements.append(req)
        counter += 1

    return requirements

def extract_requirements_with_ai_fallback(
    regulation: Regulation,
    start_index: int = 1,
) -> List[Requirement]:
    """
    Point d'entrée 'IA-ready' pour l'extraction :
    - aujourd'hui : utilise les règles simples (is_requirement_sentence, etc.)
    - demain : pourra appeler un LLM externe pour enrichir / corriger.
    """
    # Pour l'instant, on réutilise simplement la logique existante.
    return extract_requirements_from_regulation(regulation, start_index=start_index)
