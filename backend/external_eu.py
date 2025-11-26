# backend/external_eu.py
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Optional

from .schemas import Regulation


def fetch_eu_regulation_by_celex(celex_id: str) -> Optional[Regulation]:
    """
    Récupère un texte CELEX basique via EUR-Lex page HTML.
    Pas parfait, mais suffisant pour la démo.
    """
    url = f"https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:{celex_id}"

    try:
        resp = requests.get(url, timeout=12)
        resp.raise_for_status()
    except Exception as e:
        print("Erreur EUR-Lex:", e)
        return None

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find("h1") or soup.title
    title = title_tag.get_text(strip=True) if title_tag else f"Règlement UE {celex_id}"

    # très simple : on récupère tout le texte visible
    main_text = soup.get_text("\n", strip=True)
    if len(main_text) < 500:
        # trop court, on ne garde pas
        return None

    return Regulation(
        id=f"EU-{celex_id}",
        country="EU",
        title=title,
        version="1.0",
        date=datetime.utcnow(),
        text=main_text,
        url=url,
        source="EUR-Lex",
    )
