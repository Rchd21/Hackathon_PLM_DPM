# data_store.py
from datetime import datetime
from typing import Dict, List, Optional

from models import (
    Regulation,
    Requirement,
    RequirementImpact,
    RequirementHistoryItem,
)

R67_TEXT_PATH = "r67_full.txt"   # ton fichier texte complet


class InMemoryStore:
    """
    Mini base de données en mémoire centrée sur UNECE R67.
    """

    def __init__(self) -> None:
        # --- IMPORTANT : ces attributs DOIVENT exister pour éviter l’erreur ---
        self.regulations: Dict[str, Regulation] = {}
        self.requirements: Dict[str, Requirement] = {}
        self.impacts: Dict[str, RequirementImpact] = {}
        self.history: List[RequirementHistoryItem] = []

        # Charge les données R67
        self._load_r67_from_file()

    # =============================================================
    #  RÉGLEMENTATION R67 : Lecture depuis fichier texte
    # =============================================================
    def _load_r67_from_file(self) -> None:
        """
        Charge le texte complet UNECE R67 à partir du fichier r67_full.txt.
        Si le fichier est manquant, utilise une version fallback.
        """

        try:
            with open(R67_TEXT_PATH, "r", encoding="utf-8") as f:
                text = f.read().strip()
                print(f"[INFO] Texte complet R67 chargé depuis {R67_TEXT_PATH}")
        except FileNotFoundError:
            print(f"[WARNING] {R67_TEXT_PATH} introuvable → utilisation d’un texte simplifié.")
            text = (
                "UNECE Regulation No. 67 – Requirements for the approval of LPG components.\n\n"
                "Le fichier texte complet n'a pas été trouvé."
            )

        r67 = Regulation(
            id="UNECE-R67",
            country="UNECE",
            title="UNECE R67 – LPG Vehicle Equipment",
            version="1.0",
            date=datetime(2008, 2, 21),
            url="https://unece.org/transport/vehicle-regulations",
            text=text,
        )

        self.regulations[r67.id] = r67

    # =============================================================
    #     GESTION DES RÉGLEMENTATIONS
    # =============================================================
    def get_r67(self) -> Regulation:
        return self.regulations["UNECE-R67"]

    def list_regulations(self) -> List[Regulation]:
        return list(self.regulations.values())

    # =============================================================
    #     GESTION DES EXIGENCES
    # =============================================================
    def add_requirements(self, reqs: List[Requirement]) -> None:
        for r in reqs:
            self.requirements[r.id] = r
            self.history.append(
                RequirementHistoryItem(
                    timestamp=datetime.utcnow(),
                    requirement_id=r.id,
                    version=r.version,
                    change_type="created",
                    diff_summary="Created automatically",
                )
            )

    def list_requirements(self) -> List[Requirement]:
        return sorted(self.requirements.values(), key=lambda r: r.created_at)

    def get_requirements_for_regulation(self, reg_id: str) -> List[Requirement]:
        return [r for r in self.requirements.values() if r.regulation_id == reg_id]

    # =============================================================
    #     GESTION DES IMPACTS
    # =============================================================
    def save_impact(self, impact: RequirementImpact) -> None:
        self.impacts[impact.requirement_id] = impact

    def get_impact(self, req_id: str) -> Optional[RequirementImpact]:
        return self.impacts.get(req_id)

    # =============================================================
    #     HISTORIQUE
    # =============================================================
    def list_history(self) -> List[RequirementHistoryItem]:
        return sorted(self.history, key=lambda h: h.timestamp)


# Instance globale utilisée par Streamlit
store = InMemoryStore()