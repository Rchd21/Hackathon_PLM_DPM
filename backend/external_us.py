# backend/external_us.py
import requests
from datetime import datetime
from typing import List

from .schema import Regulation

FR_SEARCH_URL = "https://www.federalregister.gov/api/v1/documents"
HEADERS = {
    "User-Agent": "Renault-GPS-Reglementaire/1.0 (+https://example.com)"
}


def search_us_regulations(topic: str, limit: int = 5) -> List[Regulation]:
    params = {
        "per_page": limit,
        "order": "newest",
        "conditions[term]": topic,
    }

    try:
        resp = requests.get(FR_SEARCH_URL, params=params, headers=HEADERS, timeout=12)
        resp.raise_for_status()
        docs = resp.json().get("results", [])
    except Exception as e:
        print("Erreur Federal Register:", e)
        return []

    regs: List[Regulation] = []

    for doc in docs:
        text = (
            doc.get("body_html")
            or doc.get("body_text")
            or doc.get("abstract")
            or ""
        )

        if not text or len(text.strip()) < 150:
            continue

        reg = Regulation(
            id=f"US-FR-{doc['document_number']}",
            country="USA",
            title=doc.get("title", "Federal Rule"),
            version="1.0",
            date=datetime.fromisoformat(doc.get("publication_date", "2020-01-01")),
            text=text,
            url=doc.get("html_url"),
            source="USA-FederalRegister",
        )
        regs.append(reg)

    return regs
