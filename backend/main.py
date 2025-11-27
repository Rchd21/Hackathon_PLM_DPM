# backend/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from .store import STORE
from .schema import (
    Regulation,
    Requirement,
    RequirementImpact,
    CountryCompliance,
    ActionItem,
    HistoryItem,
)
from .nlp import extract_requirements_from_regulation
from impact import infer_impact
from external_us import search_us_regulations
from external_eu import fetch_eu_regulation_by_celex

app = FastAPI(title="GPS Réglementaire – Renault", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # pour dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Réglementations ---------- #

@app.get("/regulations", response_model=List[Regulation])
def list_regulations(
    country: Optional[str] = None,
    source: Optional[str] = None,
    q: Optional[str] = None,
):
    regs = STORE.list_regulations()
    if country:
        regs = [r for r in regs if r.country.lower() == country.lower()]
    if source:
        regs = [r for r in regs if r.source.lower() == source.lower()]
    if q:
        ql = q.lower()
        regs = [r for r in regs if ql in r.title.lower() or ql in r.text.lower()]
    return regs


@app.post("/regulations/import/us", response_model=List[Regulation])
def import_us_regulations(topic: str = Query(...), limit: int = 5):
    regs = search_us_regulations(topic, limit=limit)
    STORE.add_regulations(regs)
    return regs


@app.post("/regulations/import/eu", response_model=Regulation)
def import_eu_regulation(celex_id: str = Query(...)):
    reg = fetch_eu_regulation_by_celex(celex_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Règlement introuvable ou trop court")
    STORE.add_regulations([reg])
    return reg

# ---------- Exigences ---------- #

@app.post("/requirements/extract", response_model=List[Requirement])
def extract_requirements(regulation_id: str):
    reg = STORE.get_regulation(regulation_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Règlement inconnu")

    current_count = len(STORE.requirements)
    reqs = extract_requirements_from_regulation(reg, start_index=current_count + 1)
    STORE.add_requirements(reqs)
    return reqs


@app.get("/requirements", response_model=List[Requirement])
def list_requirements(regulation_id: Optional[str] = None):
    if regulation_id:
        return STORE.get_requirements_by_reg(regulation_id)
    return STORE.list_requirements()

# ---------- Impact ---------- #

@app.post("/impact/recompute", response_model=RequirementImpact)
def recompute_impact(requirement_id: str):
    req = STORE.requirements.get(requirement_id)
    if not req:
        raise HTTPException(status_code=404, detail="Exigence inconnue")

    impact = infer_impact(req)
    STORE.save_impact(impact)
    return impact


@app.get("/impact/{requirement_id}", response_model=RequirementImpact)
def get_impact(requirement_id: str):
    impact = STORE.get_impact(requirement_id)
    if not impact:
        raise HTTPException(status_code=404, detail="Pas d'impact calculé")
    return impact

# ---------- Dashboard ---------- #

@app.get("/dashboard/compliance", response_model=List[CountryCompliance])
def get_compliance():
    return STORE.compute_compliance_by_country()


@app.get("/dashboard/actions", response_model=List[ActionItem])
def get_actions(country: str):
    return STORE.build_actions_for_country(country)

# ---------- Historique ---------- #

@app.get("/history", response_model=List[HistoryItem])
def get_history():
    return STORE.get_history()
