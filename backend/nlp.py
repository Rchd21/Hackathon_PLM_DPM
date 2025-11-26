# backend/nlp.py
from datetime import datetime
from typing import List

from .schemas import Regulation, Requirement


def extract_requirements_from_regulation(reg: Regulation, start_index: int = 1) -> List[Requirement]:
    """
    Version simplifiée :
    - coupe le texte en phrases
    - garde 3 phrases max
    - crée des exigences 'ingénierie'
    """
    sentences = [s.strip() for s in reg.text.split(".") if s.strip()]
    sentences = sentences[:3]

    reqs: List[Requirement] = []
    idx = start_index

    for s in sentences:
        req_id = f"REQ-{idx:03d}"
        eng_text = f"[{reg.id}] Exigence {idx} – {s}"

        reqs.append(
            Requirement(
                id=req_id,
                regulation_id=reg.id,
                country=reg.country,
                version=reg.version,
                text_raw=s,
                text_engineering=eng_text,
                created_at=datetime.utcnow(),
            )
        )
        idx += 1

    return reqs
