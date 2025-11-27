// src/pages/Dashboard.jsx
import React, { useEffect, useState } from "react";

export default function Dashboard() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/dashboard")
      .then((r) => r.json())
      .then(setData);
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-[#FFCC00] mb-6">
        📊 Dashboard de conformité – Renault
      </h1>

      <table className="w-full bg-[#1a1a1a] text-white text-left rounded-xl overflow-hidden">
        <thead className="bg-[#262626] text-[#FFCC00]">
          <tr>
            <th className="p-3">Pays</th>
            <th className="p-3">Conformité (%)</th>
            <th className="p-3">Exigences suivies</th>
            <th className="p-3">Risque</th>
          </tr>
        </thead>
        <tbody>
          {data.map((p, i) => (
            <tr key={i} className="border-b border-[#333]">
              <td className="p-3">{p.Pays}</td>
              <td className="p-3">{p["Conformité (%)"]}</td>
              <td className="p-3">{p.Exigences}</td>
              <td
                className={`p-3 font-bold ${
                  p.Risque === "Élevé"
                    ? "text-red-400"
                    : p.Risque === "Moyen"
                    ? "text-yellow-400"
                    : "text-green-400"
                }`}
              >
                {p.Risque}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="text-2xl mt-10 font-bold text-[#FFCC00]">
        🔧 Actions recommandées
      </h2>

      <div className="mt-4 grid grid-cols-2 gap-6">
        {data.map((p) =>
          p.Actions?.map((a, i) => (
            <div
              key={i}
              className="p-4 bg-[#2b2b2b] rounded-xl text-white shadow"
            >
              <p className="text-[#FFCC00] font-semibold">{a.action}</p>
              <p className="text-sm opacity-80">{a.detail}</p>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
