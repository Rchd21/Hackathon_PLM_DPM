// src/pages/Impact.jsx
import React, { useEffect, useState } from "react";

export default function Impact() {
  const [requirements, setRequirements] = useState([]);
  const [selected, setSelected] = useState(null);
  const [impact, setImpact] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/requirements")
      .then((r) => r.json())
      .then(setRequirements);
  }, []);

  const fetchImpact = (reqId) => {
    fetch(`http://localhost:8000/impact/${reqId}`)
      .then((r) => r.json())
      .then(setImpact);
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-[#FFCC00] mb-6">
        🔧 Graphe d’impact – Renault
      </h1>

      <div className="bg-[#1a1a1a] p-4 rounded-xl shadow">
        <label className="text-white">Sélectionner une exigence :</label>
        <select
          className="w-full mt-2 p-2 rounded bg-[#333] text-white"
          onChange={(e) => {
            const reqId = e.target.value;
            setSelected(reqId);
            fetchImpact(reqId);
          }}
        >
          <option value="">-- Choisir --</option>
          {requirements.map((r) => (
            <option key={r.id} value={r.id}>
              {r.id} — {r.text_engineering.slice(0, 40)}…
            </option>
          ))}
        </select>
      </div>

      {impact && (
        <div className="grid grid-cols-3 gap-6 mt-10">
          {/* Composants */}
          <div className="p-6 bg-[#2b2b2b] rounded-xl shadow text-white">
            <h2 className="text-xl font-bold mb-3 text-[#FFCC00]">
              🧩 Composants impactés
            </h2>
            {impact.components.map((c) => (
              <p key={c}>• {c}</p>
            ))}
          </div>

          {/* Tests */}
          <div className="p-6 bg-[#2b2b2b] rounded-xl shadow text-white">
            <h2 className="text-xl font-bold mb-3 text-[#FFCC00]">
              🧪 Tests requis
            </h2>
            {impact.tests.map((t) => (
              <p key={t}>• {t}</p>
            ))}
          </div>

          {/* Docs */}
          <div className="p-6 bg-[#2b2b2b] rounded-xl shadow text-white">
            <h2 className="text-xl font-bold mb-3 text-[#FFCC00]">
              📄 Documents associés
            </h2>
            {impact.documents.map((d) => (
              <p key={d}>• {d}</p>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
