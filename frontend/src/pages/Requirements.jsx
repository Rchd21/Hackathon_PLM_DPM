import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function Requirements() {
  const [regs, setRegs] = useState([]);
  const [selectedRegId, setSelectedRegId] = useState("");
  const [requirements, setRequirements] = useState([]);

  useEffect(() => {
    fetch(`${API_BASE}/regulations`)
      .then((r) => r.json())
      .then((data) => {
        setRegs(data);
        if (data.length > 0) setSelectedRegId(data[0].id);
      });
  }, []);

  useEffect(() => {
    if (!selectedRegId) return;
    fetch(`${API_BASE}/requirements?regulation_id=${selectedRegId}`)
      .then((r) => r.json())
      .then(setRequirements);
  }, [selectedRegId]);

  const extract = async () => {
    if (!selectedRegId) return;
    await fetch(
      `${API_BASE}/requirements/extract?regulation_id=${selectedRegId}`,
      { method: "POST" }
    );
    const data = await fetch(
      `${API_BASE}/requirements?regulation_id=${selectedRegId}`
    ).then((r) => r.json());
    setRequirements(data);
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-xl font-semibold mb-2">
        Extraction & reformulation d’exigences
      </h1>

      <div className="flex gap-3 items-center">
        <span className="text-xs text-zinc-400">Texte réglementaire :</span>
        <select
          value={selectedRegId}
          onChange={(e) => setSelectedRegId(e.target.value)}
          className="text-xs bg-black/60 border border-zinc-700 rounded-md px-2 py-1"
        >
          {regs.map((r) => (
            <option key={r.id} value={r.id}>
              {r.country} – {r.title}
            </option>
          ))}
        </select>
        <button
          onClick={extract}
          className="text-xs px-3 py-1 rounded-md bg-renaultYellow text-black font-semibold"
        >
          🧠 Extraire des exigences
        </button>
      </div>

      <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-3">
        <h2 className="text-sm font-semibold mb-2">
          Exigences connues pour ce texte
        </h2>
        {requirements.length === 0 ? (
          <p className="text-xs text-zinc-400">
            Aucune exigence pour l’instant. Lance une extraction.
          </p>
        ) : (
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="border-b border-zinc-700">
                <th className="text-left p-1">ID</th>
                <th className="text-left p-1">Texte brut</th>
                <th className="text-left p-1">Formulation ingénierie</th>
              </tr>
            </thead>
            <tbody>
              {requirements.map((r) => (
                <tr key={r.id} className="border-b border-zinc-800">
                  <td className="p-1 align-top font-mono">{r.id}</td>
                  <td className="p-1 align-top">{r.text_raw}</td>
                  <td className="p-1 align-top text-zinc-200">
                    {r.text_engineering}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
