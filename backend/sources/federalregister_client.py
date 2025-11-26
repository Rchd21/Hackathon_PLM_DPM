import requests
from datetime import datetime

from .normalize import normalize_us_regulation

# Endpoints officiels du Federal Register
SEARCH_URL = "https://www.federalregister.gov/api/v1/documents"
ARTICLE_URL = "https://www.federalregister.gov/api/v1/articles"

HEADERS = {
    # User-Agent propre (recommandé par le Federal Register)
    "User-Agent": "GPS-Reglementaire-Hackathon/1.0 (+https://example.com)"
}


def _fetch_full_article(document_number: str) -> str:
    """
    Récupère le texte complet via l’API 'articles' du Federal Register.
    Cette API renvoie un body_html/body_text beaucoup plus riche que l’API documents.
    """
    url = f"{ARTICLE_URL}/{document_number}.json"

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        return ""

    text = (
        data.get("body_html")
        or data.get("body_text")
        or data.get("body_markdown")
        or ""
    )

    return text or ""


def search_us_regulations(topic: str, limit: int = 5):
    """
    Cherche des documents réglementaires américains (Federal Register)
    liés à un thème donné, et les renvoie sous forme de liste de Regulation.

    - Recherche par mot-clé (conditions[term])
    - Récupère le texte complet via l’API 'articles'
    - Filtre les textes trop courts pour éviter le bruit
    """
    params = {
        "per_page": limit,
        "order": "newest",
        "conditions[term]": topic,
    }

    try:
        resp = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=12)
        resp.raise_for_status()
        docs = resp.json().get("results", [])
    except Exception as e:
        raise RuntimeError(f"Erreur Federal Register : {e}")

    regs = []

    for doc in docs:
        doc_num = doc["document_number"]

        # 1) Première tentative : texte retourné directement par l’API documents
        text = (
            doc.get("body_html")
            or doc.get("body_text")
            or doc.get("body_markdown")
            or ""
        )

        # 2) Si texte trop court, on récupère l'article complet
        if not text or len(text.strip()) < 300:
            full_text = _fetch_full_article(doc_num)
            if len(full_text.strip()) > 300:
                text = full_text

        # 3) Toujours trop court ? -> on ignore ce document
        if not text or len(text.strip()) < 150:
            continue

        raw = {
            "id": f"US-FR-{doc_num}",
            "title": doc.get("title", "Federal Rule"),
            "date": doc.get("publication_date", datetime.utcnow().isoformat()),
            "text": text,
            "url": doc.get("html_url"),
            "version": "1.0",
            "source": "USA-FederalRegister",
        }

        # Transforme en objet Regulation
        regs.append(normalize_us_regulation(raw))

    return regs


