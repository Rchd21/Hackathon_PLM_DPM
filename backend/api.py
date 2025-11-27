# backend/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.store import InMemoryDataStore

app = FastAPI(title="GPS Réglementaire API")

# Autoriser le frontend React (Vite) sur http://localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STORE = InMemoryDataStore()


@app.get("/regulations")
def list_regulations():
    """Renvoie la liste des textes réglementaires en JSON simple."""
    return [
        {
            "id": r.id,
            "country": r.country,
            "title": r.title,
            "version": r.version,
            "date": r.date.isoformat(),
            "url": r.url,
        }
        for r in STORE.list_regulations()
    ]

@app.get("/history")
def get_history():
    return [
        {
            "timestamp": h.timestamp.isoformat(),
            "requirement_id": h.requirement_id,
            "version": h.version,
            "change_type": h.change_type,
            "diff_summary": h.diff_summary,
        }
        for h in STORE.get_history()
    ]
