# app.py
import streamlit as st
import pandas as pd

from data_store import store
from nlp_extractor import extract_requirements_from_text
from impact_engine import infer_impact_for_requirement


# =========================================================
#       GLOBAL APP CONFIG
# =========================================================
st.set_page_config(
    page_title="Renault – Regulatory GPS R67",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
#       SIDEBAR CSS (noir + texte blanc)
# =========================================================
st.markdown(
    """
<style>
/* Sidebar container */
section[data-testid="stSidebar"] {
    background-color: #000000 !important;   /* full black */
    padding: 2rem 1.5rem;
}

/* Tout le texte dans la sidebar en blanc + un peu plus gros */
section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
    font-size: 1.05rem;
}

/* Titre Renault plus gros et gras */
section[data-testid="stSidebar"] h1.sidebar-renault-title {
    font-size: 2.6rem;
    font-weight: 900;
    margin-top: 1rem;
    margin-bottom: 0.3rem;
}

/* Sous-titre un peu plus petit, gris clair */
section[data-testid="stSidebar"] p.sidebar-renault-subtitle {
    font-size: 1.2rem;
    color: #CCCCCC !important;
    margin-bottom: 2rem;
}

/* Titre "Navigation" un peu plus gros et gras */
section[data-testid="stSidebar"] p.sidebar-nav-title {
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 1.5rem;
    margin-bottom: 0.8rem;
}

/* Texte du menu radio : encore un peu plus grand */
section[data-testid="stSidebar"] .stRadio label p {
    font-size: 1.25rem !important;
    font-weight: 600 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
#       HELPERS
# =========================================================
def get_r67():
    return store.get_r67()


# =========================================================
#       SIDEBAR
# =========================================================
with st.sidebar:
    st.image("logo.jpg", use_container_width=True)

    st.markdown('<h1 class="sidebar-renault-title">Renault</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sidebar-renault-subtitle">Regulatory GPS – UNECE R67</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="sidebar-nav-title">Navigation</p>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "",
        [
            "1️⃣ Regulation text",
            "2️⃣ Requirement extraction",
            "3️⃣ Impact analysis",
            "4️⃣ History & traceability",
        ],
        key="nav_menu",
    )


# =========================================================
#       PAGE 1 — REGULATION TEXT
# =========================================================
if page.startswith("1️⃣"):
    reg = get_r67()

    st.title("1️⃣ Regulation text – UNECE R67")

    col_meta, col_text = st.columns([1, 2])

    with col_meta:
        st.header("Metadata")
        st.write(f"*ID:* {reg.id}")
        st.write(f"*Issuer / organisation:* {reg.country}")
        st.write(f"*Title:* {reg.title}")
        st.write(f"*Version:* {reg.version}")
        st.write(f"*Date:* {reg.date.date()}")
        st.markdown(f"[Official link]({reg.url})")

    with col_text:
        st.header("Regulation text used in the tool")
        st.info(reg.text)


# =========================================================
#       PAGE 2 — REQUIREMENT EXTRACTION
# =========================================================
elif page.startswith("2️⃣"):
    reg = get_r67()

    st.title("2️⃣ Requirement extraction – UNECE R67")

    st.subheader("Source text")
    st.info(reg.text)

    if st.button("🧠 Extract requirements using Mistral (Ollama)"):
        with st.spinner("AI extraction in progress…"):
            current_count = len(store.list_requirements())

            reqs = extract_requirements_from_text(
                reg,
                start_index=current_count + 1,
            )
            store.add_requirements(reqs)

        st.success(f"{len(reqs)} requirements extracted and stored ✔")

    reqs_for_r67 = store.get_requirements_for_regulation(reg.id)

    if reqs_for_r67:
        st.subheader("Extracted requirements (R67)")
        df = pd.DataFrame(
            [
                {
                    "ID": r.id,
                    "Raw text": r.text_raw,
                    "Engineering formulation": r.text_engineering,
                    "Created at": r.created_at,
                }
                for r in reqs_for_r67
            ]
        )
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No requirement extracted yet.")


# =========================================================
#       PAGE 3 — IMPACT ANALYSIS
# =========================================================
elif page.startswith("3️⃣"):
    st.title("3️⃣ Impact analysis – R67 → Vehicle")

    all_reqs = store.list_requirements()

    if not all_reqs:
        st.warning("No requirements available. Please extract them first (page 2).")
    else:
        label_map = {f"{r.id} – {r.text_engineering[:80]}": r.id for r in all_reqs}
        label = st.selectbox("Choose an R67 requirement", list(label_map.keys()))
        req = next(r for r in all_reqs if r.id == label_map[label])

        st.subheader("Selected requirement")
        st.write(f"*ID:* {req.id}")
        st.write(f"*Raw text:* {req.text_raw}")
        st.write(f"*Engineering version:* {req.text_engineering}")

        if st.button("🔍 Compute / update impact"):
            impact = infer_impact_for_requirement(req)
            store.save_impact(impact)
            st.success("Impact updated ✔")

        impact = store.get_impact(req.id)

        if impact:
            # --- blocs principaux --- #
            col_c, col_t, col_d = st.columns(3)

            with col_c:
                st.caption("Impacted components")
                st.write("\n".join(f"- {c}" for c in impact.components) or "—")

            with col_t:
                st.caption("Required tests")
                st.write("\n".join(f"- {t}" for t in impact.tests) or "—")

            with col_d:
                st.caption("Associated documents")
                st.write("\n".join(f"- {d}" for d in impact.documents) or "—")

            # --- Compliance matrix --- #
            st.markdown("---")
            st.subheader("Compliance matrix")

            comp_ok = len(impact.components) > 0
            test_ok = len(impact.tests) > 0
            doc_ok = len(impact.documents) > 0

            df_matrix = pd.DataFrame(
                {
                    "Criterion": [
                        "Components identified",
                        "Tests identified",
                        "Documents identified",
                    ],
                    "Status": [
                        "✅" if comp_ok else "❌",
                        "✅" if test_ok else "❌",
                        "✅" if doc_ok else "❌",
                    ],
                }
            )
            st.table(df_matrix)

            # --- Safety / validation view (optionnel, selon ton datamodel) --- #
            criticality = getattr(impact, "criticality", None)
            actions = getattr(impact, "validation_actions", None)

            if criticality or actions:
                st.subheader("Safety & validation view")
                if criticality:
                    st.write(f"*Criticality:* {criticality}")
                if actions:
                    st.write("*Suggested validation actions:*")
                    for a in actions:
                        st.write(f"- {a}")

            # --- Petit graphe de répartition --- #
            st.subheader("Impact distribution")
            df_counts = pd.DataFrame(
                {
                    "Category": ["Components", "Tests", "Documents"],
                    "Count": [
                        len(impact.components),
                        len(impact.tests),
                        len(impact.documents),
                    ],
                }
            ).set_index("Category")
            st.bar_chart(df_counts)

        st.markdown("---")
        st.subheader("Global impact summary")

        rows = []
        for r in all_reqs:
            imp = store.get_impact(r.id)
            rows.append(
                {
                    "Requirement": r.id,
                    "Components": len(imp.components) if imp else 0,
                    "Tests": len(imp.tests) if imp else 0,
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True)


# =========================================================
#       PAGE 4 — HISTORY & TRACEABILITY
# =========================================================
elif page.startswith("4️⃣"):
    st.title("4️⃣ History & traceability – R67")

    history = store.list_history()
    if not history:
        st.info("No historical data recorded yet.")
    else:
        # --- Change log --- #
        st.subheader("Change log (R67)")
        df = pd.DataFrame(
            [
                {
                    "Timestamp": h.timestamp,
                    "Requirement": h.requirement_id,
                    "Version": h.version,
                    "Change": h.change_type,
                    "Summary": h.diff_summary,
                }
                for h in history
            ]
        )
        df = df.sort_values("Timestamp")
        st.dataframe(df, use_container_width=True)

        # --- Small stats --- #
        st.markdown("---")
        st.subheader("History statistics")

        st.write(f"- *Total changes:* {len(df)}")
        st.write(f"- *Distinct requirements impacted:* {df['Requirement'].nunique()}")

        counts_by_change = df["Change"].value_counts()
        st.write("*Changes by type:*")
        st.bar_chart(counts_by_change)

    st.markdown("---")
    st.caption(
        "In a real industrial context at Renault, this page would provide audit-proof "
        "traceability for all regulatory requirements and their evolution."
    )