from typing import List, Dict
from .data_store import InMemoryDataStore


def build_country_dashboard(store: InMemoryDataStore) -> List[Dict]:
    """
    Construit une vue synthétique de conformité par pays.
    """
    rows: List[Dict] = []
    countries = sorted({r.country for r in store.requirements.values()}) or []

    for country in countries:
        compliance, nonconf = store.compute_compliance_for_country(country)
        if compliance >= 90:
            risk = "Faible"
        elif compliance >= 70:
            risk = "Moyen"
        else:
            risk = "Élevé"

        rows.append(
            {
                "Pays": country,
                "Conformité (%)": compliance,
                "Risque": risk,
                "Exigences non conformes": len(nonconf),
            }
        )
    return rows


def build_actions_for_country(store: InMemoryDataStore, country: str) -> List[Dict]:
    """
    Génère une liste d'actions recommandées pour un pays donné,
    à partir des exigences non conformes.
    """
    compliance, nonconf = store.compute_compliance_for_country(country)
    actions: List[Dict] = []

    for req_id in nonconf:
        req = store.requirements.get(req_id)
        if not req:
            continue
        impact = store.get_impact(req_id)

        if impact and impact.tests:
            tests_str = ", ".join(impact.tests)
            comps_str = ", ".join(impact.components) if impact.components else "N/A"
            action_text = (
                f"Planifier / relancer les tests [{tests_str}] "
                f"pour les composants [{comps_str}] afin de couvrir l'exigence {req_id}."
            )
        else:
            action_text = (
                f"Analyser en détail l'exigence {req_id} et définir les tests associés "
                f"pour le marché {country}."
            )

        actions.append(
            {
                "Exigence": req_id,
                "Pays": country,
                "Texte (résumé)": (req.text_engineering or req.text_raw)[:80] + "...",
                "Action recommandée": action_text,
            }
        )

    return actions
