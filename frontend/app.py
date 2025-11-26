import os
import sys

# Ajoute la racine du projet au PYTHONPATH,
# même si tu lances "streamlit run frontend/app.py" depuis le dossier frontend.
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)



import streamlit as st
import pandas as pd

from backend.data_store import InMemoryDataStore
from backend.nlp_extractor import extract_requirements_from_regulation
from backend.impact_engine import infer_impacts_for_requirement
from backend.dashboard_utils import (
    build_country_dashboard,
    build_actions_for_country,
)

# --- Initialisation du store en session --- #

if "store" not in st.session_state:
    st.session_state.store = InMemoryDataStore()

store = st.session_state.store

st.set_page_config(
    page_title="GPS Réglementaire",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- Sidebar navigation --- #
st.sidebar.image("Logo-ESILV.jpg", use_container_width=True)
st.sidebar.title("GPS Réglementaire")
page = st.sidebar.radio(
    "Navigation",
    [
        "1️⃣ Veille & Textes",
        "2️⃣ Extraction d'exigences (NLP)",
        "3️⃣ Graphe d'impact",
        "4️⃣ Dashboard de conformité",
        "5️⃣ Historique & traçabilité",
    ],
)


# --- Helpers UI --- #

def show_regulation_selector():
    regs = store.list_regulations()
    if not regs:
        st.info("Aucun texte réglementaire connu pour l'instant.")
        return None

    options = {f"{r.country} - {r.title} (v{r.version})": r.id for r in regs}
    label = st.selectbox("Choisir un texte réglementaire", list(options.keys()))
    return store.get_regulation(options[label])


# --- Page 1 : Veille réglementaire & textes --- #

if page.startswith("1️⃣"):
    st.title("1️⃣ Veille réglementaire & Textes")
    st.write(
        "Visualisation des textes réglementaires surveillés et détection des versions."
    )

    col_list, col_detail = st.columns([1, 2])

    with col_list:
        regs = store.list_regulations()
        if regs:
            df = pd.DataFrame(
                [
                    {
                        "ID": r.id,
                        "Pays": r.country,
                        "Titre": r.title,
                        "Version": r.version,
                        "Date": r.date.date(),
                        "Version précédente": r.previous_version_id,
                    }
                    for r in regs
                ]
            )
            st.subheader("Textes surveillés")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Aucun texte réglementaire pour l'instant.")

    with col_detail:
        st.subheader("Détail d'un texte")
        reg = show_regulation_selector()
        if reg:
            st.markdown(f"*ID :* `{reg.id}`")
            st.markdown(f"*Pays :* {reg.country}")
            st.markdown(f"*Version :* {reg.version}")
            st.markdown(f"*Date :* {reg.date.date()}")
            if reg.url:
                st.markdown(f"[Lien officiel]({reg.url})")
            st.markdown("*Texte brut :*")
            st.info(reg.text)

            if reg.previous_version_id:
                prev = store.get_regulation(reg.previous_version_id)
                if prev:
                    st.markdown("### Diff simplifiée avec la version précédente")
                    st.write(
                        "⚠ Démo : on affiche juste les deux textes côte à côte "
                        "(dans un vrai produit on ferait un diff plus intelligent)."
                    )
                    col_prev, col_new = st.columns(2)
                    with col_prev:
                        st.caption(f"Version précédente ({prev.version})")
                        st.text(prev.text)
                    with col_new:
                        st.caption(f"Version actuelle ({reg.version})")
                        st.text(reg.text)

        st.markdown("---")
        st.markdown("### 🔗 Connexion à des sources réelles")

        col_eu, col_us = st.columns(2)

        with col_eu:
            st.caption("Importer un texte UE (EUR-Lex / CELEX)")
            celex_id = st.text_input(
                "ID CELEX (ex: 32014R0535)",
                key="celex_input",
                placeholder="32014R0535",
            )
            if st.button("Importer depuis l'UE", key="btn_import_eu"):
                if celex_id.strip():
                    try:
                        reg = store.import_eu_regulation(celex_id.strip())
                        st.success(f"Importé : {reg.id} – {reg.title}")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de l'import UE : {e}")
                else:
                    st.warning("Merci de saisir un ID CELEX.")

        with col_us:
            st.caption("Importer des textes US (Federal Register)")
            topic = st.text_input(
                "Mot-clé (ex: airbag, battery…)",
                key="us_topic_input",
                placeholder="airbag",
            )
            limit = st.slider(
                "Nombre de textes à importer", min_value=1, max_value=10, value=3
            )
            if st.button("Importer depuis les USA", key="btn_import_us"):
                if topic.strip():
                    try:
                        regs = store.import_us_regulations_by_topic(
                            topic.strip(), limit=limit
                        )
                        st.success(f"{len(regs)} textes US importés.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erreur lors de l'import US : {e}")
                else:
                    st.warning("Merci de saisir un mot-clé.")

# --- Page 2 : Extraction d'exigences --- #

elif page.startswith("2️⃣"):
    st.title("2️⃣ Extraction & Reformulation d'exigences (NLP)")

    reg = show_regulation_selector()
    if reg:
        st.markdown("### Texte réglementaire sélectionné")
        st.info(reg.text)

        st.markdown("### Extraction automatique")
        if st.button("🧠 Extraire les exigences pour ce texte"):
            # Pour ne pas recréer des IDs déjà existants, on prend le nombre actuel
            current_count = len(store.requirements)
            reqs = extract_requirements_from_regulation(
                reg, start_index=current_count + 1
            )
            store.add_requirements(reqs)
            st.success(f"{len(reqs)} exigences extraites et stockées.")

        reqs_for_reg = store.get_requirements_by_reg(reg.id)
        if reqs_for_reg:
            df_reqs = pd.DataFrame(
                [
                    {
                        "ID": r.id,
                        "Pays": r.country,
                        "Version": r.version,
                        "Texte brut": r.text_raw,
                        "Formulation ingénierie": r.text_engineering,
                    }
                    for r in reqs_for_reg
                ]
            )
            st.markdown("### Exigences connues pour ce texte")
            st.dataframe(df_reqs, use_container_width=True)
        else:
            st.info("Aucune exigence extraite pour ce texte pour l'instant.")
    else:
        st.info("Commence par importer / sélectionner un texte sur la page 1.")

# --- Page 3 : Graphe d'impact --- #

elif page.startswith("3️⃣"):
    st.title("3️⃣ Graphe d'impact Produit ↔ Exigences")

    all_reqs = store.list_requirements()
    if not all_reqs:
        st.warning("Aucune exigence connue. Commence par la page 2 (NLP).")
    else:
        req_labels = {
            f"{r.id} - {r.text_engineering[:60]}...": r.id for r in all_reqs
        }
        label = st.selectbox("Choisir une exigence", list(req_labels.keys()))
        req_id = req_labels[label]
        req = store.requirements[req_id]

        st.markdown("### Détail de l'exigence")
        st.write(f"*ID :* `{req.id}`")
        st.write(f"*Pays :* {req.country}")
        st.write(f"*Texte :* {req.text_engineering}")

        if st.button("🧮 Calculer / recalculer l'impact"):
            impact = infer_impacts_for_requirement(req, store)
            store.save_impact(impact)
            st.success("Impact mis à jour.")

        impact = store.get_impact(req.id)
        if impact:
            st.markdown("### Impact sur le produit")

            col_c, col_t, col_d = st.columns(3)

            with col_c:
                st.caption("Composants impactés")
                for c_id in impact.components:
                    comp = store.components.get(c_id)
                    st.write(f"- `{c_id}` – {comp.name if comp else ''}")

            with col_t:
                st.caption("Tests requis")
                for t_id in impact.tests:
                    test = store.tests.get(t_id)
                    st.write(f"- `{t_id}` – {test.name if test else ''}")

            with col_d:
                st.caption("Documents associés")
                for doc in impact.documents:
                    st.write(f"- `{doc}`")
        else:
            st.info("Aucun impact calculé pour cette exigence pour l'instant.")

        st.markdown("---")
        st.markdown("### Synthèse des impacts connus")
        rows = []
        for r in all_reqs:
            imp = store.get_impact(r.id)
            rows.append(
                {
                    "Exigence": r.id,
                    "Pays": r.country,
                    "Nb composants": len(imp.components) if imp else 0,
                    "Nb tests": len(imp.tests) if imp else 0,
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True)

# --- Page 4 : Dashboard de conformité --- #

elif page.startswith("4️⃣"):
    st.title("4️⃣ Dashboard de conformité")

    if not store.requirements:
        st.warning("Aucune exigence connue. Commence par la page 2 (NLP).")
    else:
        st.markdown("### Vue globale par pays")
        rows = build_country_dashboard(store)
        df_dash = pd.DataFrame(rows)
        st.dataframe(df_dash, use_container_width=True)

        st.markdown("### Détail par pays")
        countries = [r["Pays"] for r in rows]
        if countries:
            country = st.selectbox("Choisir un pays", countries)
            compliance, nonconf = store.compute_compliance_for_country(country)
            st.write(f"*Conformité :* {compliance} %")

            if nonconf:
                st.error(f"{len(nonconf)} exigences non conformes :")
                for req_id in nonconf:
                    r = store.requirements[req_id]
                    st.markdown(f"- `{req_id}` – {r.text_engineering}")
            else:
                st.success("Aucune exigence non conforme détectée pour ce pays.")

            st.markdown("### Actions recommandées")
            actions = build_actions_for_country(store, country)
            if actions:
                df_actions = pd.DataFrame(actions)
                st.dataframe(df_actions, use_container_width=True)
            else:
                st.info("Aucune action recommandée (toutes les exigences connues sont couvertes).")

        st.markdown("---")
        st.markdown("### Produit couvert")
        st.json(
            {
                "product_id": store.product.id,
                "name": store.product.name,
                "markets": store.product.markets,
                "tests": store.product.tests,
            }
        )

# --- Page 5 : Historique & traçabilité --- #

elif page.startswith("5️⃣"):
    st.title("5️⃣ Historique & traçabilité")

    history = store.get_history()
    if not history:
        st.info("Aucune entrée d'historique pour l'instant.")
    else:
        df_hist = pd.DataFrame(
            [
                {
                    "Horodatage": h.timestamp,
                    "Exigence": h.requirement_id,
                    "Version": h.version,
                    "Type de changement": h.change_type,
                    "Résumé": h.diff_summary,
                }
                for h in history
            ]
        )
        st.dataframe(df_hist.sort_values("Horodatage"), use_container_width=True)

    st.markdown("---")
    st.markdown(
        "Dans un vrai projet, cette page permettrait de justifier chaque décision "
        "face à un auditeur : qui a modifié quoi, quand, et pourquoi."
    )
