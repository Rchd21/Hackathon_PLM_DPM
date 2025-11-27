// src/pages/History.jsx
import React, { useEffect, useState } from "react";

export default function History() {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/history")
      .then((r) => r.json())
      .then(setHistory);
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold text-[#FFCC00] mb-6">
        📜 Historique & traçabilité – Renault
      </h1>

      <table className="w-full bg-[#1a1a1a] text-white text-left rounded-xl overflow-hidden">
        <thead className="bg-[#262626] text-[#FFCC00]">
          <tr>
            <th className="p-3">Horodatage</th>
            <th className="p-3">Exigence</th>
            <th className="p-3">Version</th>
            <th className="p-3">Type</th>
            <th className="p-3">Résumé</th>
          </tr>
        </thead>

        <tbody>
          {history.map((h, i) => (
            <tr key={i} className="border-b border-[#333]">
              <td className="p-3">{h.timestamp}</td>
              <td className="p-3 font-semibold">{h.requirement_id}</td>
              <td className="p-3">{h.version}</td>
              <td className="p-3">{h.change_type}</td>
              <td className="p-3">{h.diff_summary}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
