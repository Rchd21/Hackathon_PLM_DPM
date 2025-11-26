from typing import List, Dict
from backend.data_store import InMemoryDataStore


def build_country_dashboard(store: InMemoryDataStore) -> List[Dict]:
    rows = []
    for country in sorted({r.country for r in store.requirements.values()}):
        compliance, nonconf = store.compute_compliance_for_country(country)
        if compliance >= 90:
            risk = "Low"
        elif compliance >= 70:
            risk = "Medium"
        else:
            risk = "High"

        rows.append(
            {
                "Pays": country,
                "Conformité (%)": compliance,
                "Risque": risk,
                "Exigences non conformes": len(nonconf),
            }
        )
    return rows