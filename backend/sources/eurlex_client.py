import requests
from datetime import datetime
from backend.sources.normalize import normalize_eu_regulation


# Point d’accès REST simplifié (EUR-Lex / Cellar)
# Voir documentation officielle pour endpoints SPARQL ou REST.
BASE_URL = "https://eur-lex.europa.eu/EURLexWebService"


def fetch_eu_regulation_by_celex(celex_id: str) -> dict:
    """
    Récupère une réglementation UE via son CELEX ID.
    Renvoie un dictionnaire brut, normalisé ensuite par normalize_eu_regulation().
    """

    # Appel simplifié (l’API réelle requiert SPARQL / headers spécifiques)
    params = {
        "celex": celex_id,
        "format": "json"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        raise RuntimeError(f"Erreur lors de l'accès à EUR-Lex : {e}")

    # Extraction simplifiée :
    raw = {
        "id": f"EU-{celex_id}",
        "title": data.get("title", "Règlement UE inconnu"),
        "date": data.get("date", datetime.utcnow().isoformat()),
        "text": data.get("text", ""),
        "url": data.get("url", f"https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX:{celex_id}"),
        "version": data.get("version", "1.0"),
    }
    return raw


def get_eu_regulation(celex_id: str):
    """
    Renvoie directement un objet Regulation.
    """
    raw = fetch_eu_regulation_by_celex(celex_id)
    return normalize_eu_regulation(raw)
