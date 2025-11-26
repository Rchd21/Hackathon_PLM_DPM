from datetime import datetime
from backend.models import Regulation


def normalize_eu_regulation(raw: dict) -> Regulation:
    """
    Transforme une réponse EUR-Lex/Cellar en objet Regulation.
    Le dict `raw` doit contenir au minimum : id, title, date, text, url.
    """
    return Regulation(
        id=raw.get("id"),
        title=raw.get("title", "Règlement UE"),
        country="EU",
        version=raw.get("version", "1.0"),
        date=datetime.fromisoformat(raw["date"]),
        url=raw.get("url"),
        text=raw.get("text", ""),
        previous_version_id=raw.get("previous_version_id"),
        domain="international",
        scope="product_safety"
    )


def normalize_us_regulation(raw: dict) -> Regulation:
    """
    Transforme une réponse Federal Register en Regulation.
    """
    return Regulation(
        id=raw.get("id"),
        title=raw.get("title", "Federal Rule"),
        country="USA",
        version=raw.get("version", "1.0"),
        date=datetime.fromisoformat(raw["date"]),
        url=raw.get("url"),
        text=raw.get("text", ""),
        previous_version_id=None,
        domain="international",
        scope="product_safety"
    )
