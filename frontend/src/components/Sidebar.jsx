import { NavLink } from "react-router-dom";

const navLinkClass =
  "block px-4 py-2 rounded-md text-sm font-medium hover:bg-zinc-800";
const activeClass = "bg-zinc-800 text-renaultYellow";

export default function Sidebar() {
  return (
    <aside className="w-64 bg-black/90 border-r border-zinc-800 flex flex-col">
      <div className="px-4 py-4 flex items-center gap-2 border-b border-zinc-800">
        <div className="w-4 h-4 border-2 border-renaultYellow rotate-45" />
        <div>
          <div className="text-xs text-zinc-400 uppercase tracking-widest">
            Renault
          </div>
          <div className="text-sm font-semibold">GPS Réglementaire</div>
        </div>
      </div>
      <nav className="p-3 space-y-1">
        <NavLink
          to="/regulations"
          className={({ isActive }) =>
            `${navLinkClass} ${isActive ? activeClass : ""}`
          }
        >
          Veille & Textes
        </NavLink>
        <NavLink
          to="/requirements"
          className={({ isActive }) =>
            `${navLinkClass} ${isActive ? activeClass : ""}`
          }
        >
          Exigences (NLP)
        </NavLink>
        <NavLink
          to="/impact"
          className={({ isActive }) =>
            `${navLinkClass} ${isActive ? activeClass : ""}`
          }
        >
          Impact produit
        </NavLink>
        <NavLink
          to="/dashboard"
          className={({ isActive }) =>
            `${navLinkClass} ${isActive ? activeClass : ""}`
          }
        >
          Dashboard conformité
        </NavLink>
        <NavLink
          to="/history"
          className={({ isActive }) =>
            `${navLinkClass} ${isActive ? activeClass : ""}`
          }
        >
          Traçabilité
        </NavLink>
      </nav>
      <div className="mt-auto p-3 text-xs text-zinc-500">
        © 2025 – Démo interne Renault
      </div>
    </aside>
  );
}
