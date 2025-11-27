// frontend/src/App.jsx
import React, { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000"; // ton backend FastAPI

export default function App() {
  const [regs, setRegs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function load() {
      try {
        // 🚀 CORRECTION : backticks ` ` obligatoires !
        const res = await fetch(`${API_URL}/regulations`);

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`);
        }

        const data = await res.json();
        setRegs(data);
      } catch (e) {
        console.error("Erreur fetch /regulations :", e);
        setError(String(e));
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return (
    <div className="min-h-screen bg-renaultDark text-renaultGrey">
      {/* Header */}
      <header className="border-b border-gray-700 px-8 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-renaultYellow">
            GPS Réglementaire – Renault
          </h1>
          <p className="text-sm text-gray-300">
            Vue simplifiée pour vérifier la connexion front ↔ back
          </p>
        </div>
        <span className="text-xs text-gray-400">
          Backend : {API_URL}
        </span>
      </header>

      {/* Contenu */}
      <main className="p-8 max-w-5xl mx-auto">
        {loading && <p>⏳ Chargement des textes réglementaires…</p>}

        {error && (
          <div className="mb-4 p-4 rounded bg-red-900/40 border border-red-500 text-red-200">
            <strong>Erreur de connexion au backend :</strong>
            <br />
            {error}
          </div>
        )}

        {!loading && !error && (
          <>
            <h2 className="text-xl font-semibold text-renaultYellow mb-4">
              Textes réglementaires connus
            </h2>

            {regs.length === 0 ? (
              <p className="text-gray-300">
                Aucun texte reçu du backend. Vérifie ton store ou ajoute des données.
              </p>
            ) : (
              <div className="space-y-3">
                {regs.map((r) => (
                  <div
                    key={r.id}
                    className="p-4 rounded-lg bg-[#111827] border border-gray-700"
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="text-sm text-gray-400">
                          {r.country} • v{r.version} • {r.date?.slice(0, 10)}
                        </p>
                        <h3 className="text-lg font-semibold text-white">
                          {r.title}
                        </h3>
                      </div>

                      {r.url && (
                        <a
                          href={r.url}
                          target="_blank"
                          rel="noreferrer"
                          className="text-xs text-renaultYellow underline"
                        >
                          Ouvrir
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}