import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_eu_regulation(celex_id: str):
    """
    Récupère un texte CELEX depuis EUR-Lex en HTML
    et en extrait le texte brut.
    """

    url = f"https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:{celex_id}"

    resp = requests.get(url, timeout=12)
    if resp.status_code != 200:
        raise RuntimeError(f"Erreur EUR-Lex : statut {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Trouver le bloc du texte principal
    text_block = soup.find("div", {"class": "tab-content"})

    if not text_block:
        # fallback : prendre tout le texte
        full_text = soup.get_text("\n")
    else:
        full_text = text_block.get_text("\n")

    # Construire l’objet Regulation
    from backend.models import Regulation

    return Regulation(
        id=f"EU-{celex_id}",
        country="EU",
        title=f"EU Regulation {celex_id}",
        version="1.0",
        date=datetime.utcnow(),
        text=full_text.strip(),
        url=url
    )
