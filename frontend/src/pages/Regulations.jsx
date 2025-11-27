import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function Regulations() {
  const [regs, setRegs] = useState([]);
  const [selected, setSelected] = useState(null);
  const [usTopic, setUsTopic] = useState("battery");
  const [celex, setCelex] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/regulations`)
      .then((r) => r.json())
      .then((data) => {
        setRegs(data);
        if (data.length > 0) setSelected(data[0]);
      });
  }, []);

  const onSelect = (reg) => {
    setSelected(reg);
  };

  const importUS = async () => {
    if (!usTopic.trim()) return;
    const url = `${API_BASE}/regulations/import/us?topic=${encodeURIComponent(
      usTopic
    )}&limit=5`;
    const res = await fetch(url, { method: "POST" });
    if (res.ok) {
      const data = await fetch(`${API_BASE}/regulations`).then((r) => r.json());
      setRegs(data);
    }
  };

  const importEU = async () => {
    if (!celex.trim()) return;
    const url = `${API_BASE}/regulations/import/eu?celex_id=${encodeURIComponent(
      celex
    )}`;
    const res = await fetch(url, { method: "POST" });
    if (res.ok) {
      const data = await fetch(`${API_BASE}/regulations`).then((r) => r.json());
      setRegs(data);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-semibold mb-2">
        Veille réglementaire automobile (monde)
      </h1>

      <div className="grid grid-cols-3 gap-4">
        {/* Liste des textes */}
        <div className="col-span-1 bg-zinc-900/60 border border-zinc-800 rounded-lg p-3">
          <div className="flex justify-between items-center mb-2">
            <h2 className="text-sm font-semibold">Textes surveillés</h2>
            <span className="text-xs text-zinc-400">
              {regs.length} textes
            </span>
          </div>
          <div className="space-y-1 max-h-[480px] overflow-y-auto">
            {regs.map((r) => (
              <button
                key={r.id}
                className={`w-full text-left px-2 py-1 rounded-md text-xs hover:bg-zinc-800 ${
                  selected && selected.id === r.id
                    ? "bg-zinc-800 border border-renaultYellow/40"
                    : ""
                }`}
                onClick={() => onSelect(r)}
              >
                <div className="font-medium">
                  {r.country} · {r.title}
                </div>
                <div className="text-[10px] text-zinc-400">
                  {r.id} · {r.source}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Détail */}
        <div className="col-span-2 space-y-4">
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4">
            <h2 className="text-sm font-semibold mb-2">
              Détail du texte sélectionné
            </h2>
            {selected ? (
              <>
                <p className="text-xs">
                  <span className="font-semibold">ID :</span> {selected.id}
                </p>
                <p className="text-xs">
                  <span className="font-semibold">Pays / org :</span>{" "}
                  {selected.country}
                </p>
                <p className="text-xs">
                  <span className="font-semibold">Source :</span>{" "}
                  {selected.source}
                </p>
                <p className="text-xs">
                  <span className="font-semibold">Titre :</span>{" "}
                  {selected.title}
                </p>
                {selected.url && (
                  <p className="text-xs mt-1">
                    <a
                      href={selected.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-renaultYellow underline"
                    >
                      Ouvrir la source officielle
                    </a>
                  </p>
                )}
                <div className="mt-3 max-h-64 overflow-y-auto text-xs text-zinc-200 whitespace-pre-wrap border border-zinc-800 rounded-md p-2 bg-black/40">
                  {selected.text}
                </div>
              </>
            ) : (
              <p className="text-xs text-zinc-400">Aucun texte sélectionné.</p>
            )}
          </div>

          {/* Import monde */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-2">
                Import USA (Federal Register)
              </h3>
              <p className="text-xs text-zinc-400 mb-2">
                Recherche par sujet (ex: <code>battery</code>,{" "}
                <code>airbag</code>, <code>cybersecurity</code>…)
              </p>
              <div className="flex gap-2">
                <input
                  value={usTopic}
                  onChange={(e) => setUsTopic(e.target.value)}
                  className="flex-1 text-xs rounded-md bg-black/50 border border-zinc-700 px-2 py-1"
                  placeholder="battery"
                />
                <button
                  onClick={importUS}
                  className="text-xs px-3 py-1 rounded-md bg-renaultYellow text-black font-semibold"
                >
                  Importer USA
                </button>
              </div>
            </div>

            <div className="bg-zinc-900/60 border border-zinc-800 rounded-lg p-4">
              <h3 className="text-sm font-semibold mb-2">
                Import UE par CELEX (EUR-Lex)
              </h3>
              <p className="text-xs text-zinc-400 mb-2">
                Exemple : <code>32023R1542</code> pour le règlement batteries.
              </p>
              <div className="flex gap-2">
                <input
                  value={celex}
                  onChange={(e) => setCelex(e.target.value)}
                  className="flex-1 text-xs rounded-md bg-black/50 border border-zinc-700 px-2 py-1"
                  placeholder="32023R1542"
                />
                <button
                  onClick={importEU}
                  className="text-xs px-3 py-1 rounded-md bg-renaultYellow text-black font-semibold"
                >
                  Importer UE
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
