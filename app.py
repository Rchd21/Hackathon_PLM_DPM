# app.py
import streamlit as st
import pandas as pd

from data_store import store
from nlp_extractor import extract_requirements_from_text
from impact_engine import infer_impact_for_requirement

# =========================================================
#  APP CONFIG
# =========================================================
st.set_page_config(
    page_title="Renault – R67 Regulatory GPS",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
#  GLOBAL CSS STYLING (DARK SIDEBAR, WHITE TEXT)
# =========================================================
st.markdown(
    """
    <style>
    /* ---- SIDEBAR ---- */
    [data-testid="stSidebar"] {
        background-color: #050505 !important;
    }

    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }

    .sidebar-title-renault {
        font-size: 28px;
        font-weight: 800;
        margin-top: 0.5rem;
        margin-bottom: 1.5rem;
        color: #FFFFFF;
    }

    .sidebar-radio-label > div:nth-child(1) {
        font-size: 16px !important;
        font-weight: 500 !important;
        color: #FFFFFF !important;
    }

    /* ---- MAIN AREA ---- */
    .main-title {
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 22px;
        font-weight: 700;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
#  SIDEBAR LAYOUT
# =========================================================
with st.sidebar:
    try:
        st.image("logo.jpg", use_container_width=True)
    except Exception:
        st.write("")  # ignore if logo missing

    st.markdown('<div class="sidebar-title-renault">Renault – R67 Regulatory GPS</div>', unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "1️⃣ Regulation text",
            "2️⃣ Requirement extraction",
            "3️⃣ Impact analysis",
            "4️⃣ History & traceability",
            "5️⃣ Compliance dashboard",
        ],
        key="nav_radio",
    )

# =========================================================
#  HELPERS
# =========================================================
def get_r67():
    return store.get_r67()


# =========================================================
#  PAGE 1 — REGULATION TEXT
# =========================================================
if page.startswith("1️⃣"):
    reg = get_r67()

    st.markdown(
        "<div class='main-title'>1️⃣ Regulation text — UNECE R67</div>",
        unsafe_allow_html=True,
    )

    col_meta, col_text = st.columns([1, 2])

    with col_meta:
        st.markdown("<div class='section-title'>Metadata</div>", unsafe_allow_html=True)
        st.markdown(f"*ID:* {reg.id}")
        st.markdown(f"*Authority:* {reg.country}")
        st.markdown(f"*Title:* {reg.title}")
        st.markdown(f"*Version:* {reg.version}")
        st.markdown(f"*Date:* {reg.date.date()}")
        st.markdown(f"[Official link]({reg.url})")

    with col_text:
        st.markdown(
            "<div class='section-title'>Full regulatory text used in the tool</div>",
            unsafe_allow_html=True,
        )
        st.info(reg.text)


# =========================================================
#  PAGE 2 — REQUIREMENT EXTRACTION
# =========================================================
elif page.startswith("2️⃣"):
    reg = get_r67()

    st.markdown(
        "<div class='main-title'>2️⃣ Requirement extraction & engineering reformulation</div>",
        unsafe_allow_html=True,
    )

    st.write(
        "This page uses a local LLM (Mistral via Ollama) to extract **atomic, "
        "testable engineering requirements** from the UNECE R67 regulation text."
    )

    # ---- Extraction section FIRST ----
    st.markdown("<div class='section-title'>⚙ Run AI-based extraction</div>", unsafe_allow_html=True)

    if st.button("🧠 Extract requirements from R67 with Mistral (Ollama)"):
        with st.spinner("Running the AI extraction…"):
            current_count = len(store.list_requirements())
            reqs = extract_requirements_from_text(
                reg,
                start_index=current_count + 1,
            )
            store.add_requirements(reqs)

        st.success(f"{len(reqs)} requirements extracted and stored ✔")

    # ---- Preview of source text (collapsible) ----
    with st.expander("Show R67 source text (for context)", expanded=False):
        st.info(reg.text)

    # ---- Display extracted requirements ----
    reqs_for_r67 = store.get_requirements_for_regulation(reg.id)

    st.markdown("<div class='section-title'>📄 Extracted requirements (UNECE R67)</div>", unsafe_allow_html=True)

    if reqs_for_r67:
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
        st.info("No requirements have been extracted yet. Click the button above to run the AI extraction.")


# =========================================================
#  PAGE 3 — IMPACT ANALYSIS
# =========================================================
elif page.startswith("3️⃣"):
    st.markdown(
        "<div class='main-title'>3️⃣ Impact analysis — R67 requirement → vehicle architecture</div>",
        unsafe_allow_html=True,
    )

    all_reqs = store.list_requirements()
    if not all_reqs:
        st.warning("No requirements available. Please run the extraction on page 2 first.")
    else:
        # --- Requirement selector ---
        label_map = {
            f"{r.id} – {r.text_engineering[:90]}": r.id
            for r in all_reqs
        }
        selected_label = st.selectbox("Select a R67 requirement", list(label_map.keys()))
        req = next(r for r in all_reqs if r.id == label_map[selected_label])

        # --- Requirement details ---
        st.markdown("<div class='section-title'>Selected requirement</div>", unsafe_allow_html=True)
        st.write(f"*ID:* {req.id}")
        st.write(f"*Raw text:* {req.text_raw}")
        st.write(f"*Engineering formulation:* {req.text_engineering}")

        # --- Compute / refresh impact ---
        if st.button("🔍 Compute / refresh impact for this requirement"):
            st.info("[IMPACT] Calling Mistral/Ollama to infer impacted components & tests…")
            impact = infer_impact_for_requirement(req)
            store.save_impact(impact)
            st.success("Impact updated ✔")

        impact = store.get_impact(req.id)

        if impact:
            st.markdown(
                "<div class='section-title'>Impact on architecture & validation</div>",
                unsafe_allow_html=True,
            )

            col_c, col_t, col_d = st.columns(3)

            with col_c:
                st.caption("Impacted components")
                if impact.components:
                    for c in impact.components:
                        st.write(f"- {c}")
                else:
                    st.write("—")

            with col_t:
                st.caption("Required tests / validations")
                if impact.tests:
                    for t in impact.tests:
                        st.write(f"- {t}")
                else:
                    st.write("—")

            with col_d:
                st.caption("Related evidences / documents")
                if impact.documents:
                    for d in impact.documents:
                        st.write(f"- {d}")
                else:
                    st.write("—")

            st.markdown("*Criticality:* " + impact.criticality)
            if impact.validation_actions:
                st.markdown("*Suggested V&V actions:*")
                for a in impact.validation_actions:
                    st.write(f"- {a}")
        else:
            st.info("No impact has been computed yet for this requirement.")

        # --- Global synthesis table ---
        st.markdown("---")
        st.markdown("<div class='section-title'>Global synthesis of known impacts</div>", unsafe_allow_html=True)

        rows = []
        for r in all_reqs:
            imp = store.get_impact(r.id)
            rows.append(
                {
                    "Requirement": r.id,
                    "Nb components": len(imp.components) if imp else 0,
                    "Nb tests": len(imp.tests) if imp else 0,
                    "Criticality": imp.criticality if imp else "",
                }
            )

        df_imp = pd.DataFrame(rows)
        st.dataframe(df_imp, use_container_width=True)

        # Small bar chart: number of tests per requirement
        if not df_imp.empty:
            st.markdown("#### Tests per requirement")
            st.bar_chart(df_imp.set_index("Requirement")["Nb tests"])


# =========================================================
#  PAGE 4 — HISTORY & TRACEABILITY
# =========================================================
elif page.startswith("4️⃣"):
    st.markdown(
        "<div class='main-title'>4️⃣ History & traceability</div>",
        unsafe_allow_html=True,
    )

    history = store.list_history()
    if not history:
        st.info("No history entries yet.")
    else:
        df_hist = pd.DataFrame(
            [
                {
                    "Timestamp": h.timestamp,
                    "Requirement": h.requirement_id,
                    "Version": h.version,
                    "Change type": h.change_type,
                    "Summary": h.diff_summary,
                }
                for h in history
            ]
        )
        st.dataframe(df_hist.sort_values("Timestamp"), use_container_width=True)

    st.markdown("---")
    st.caption(
        "In a real Renault context, this page would provide full traceability for audits: "
        "who changed what, when, and why."
    )


# =========================================================
#  PAGE 5 — COMPLIANCE DASHBOARD (EU / INDIA / JAPAN)
# =========================================================
elif page.startswith("5️⃣"):
    st.markdown(
        "<div class='main-title'>5️⃣ Compliance dashboard — markets comparison</div>",
        unsafe_allow_html=True,
    )

    st.write(
        "This page lets you manually annotate each R67 requirement with a compliance status "
        "for different markets (EU, India, Japan) and provides a quick dashboard view."
    )

    all_reqs = store.list_requirements()
    if not all_reqs:
        st.warning("No requirements available. Please run the extraction on page 2 first.")
    else:
        # --- Requirement selector for editing compliance ---
        st.markdown("<div class='section-title'>Edit compliance for a requirement</div>", unsafe_allow_html=True)

        label_map = {f"{r.id} – {r.text_engineering[:80]}": r.id for r in all_reqs}
        selected_label = st.selectbox("Select a requirement", list(label_map.keys()))
        req = next(r for r in all_reqs if r.id == label_map[selected_label])

        col_eu, col_in, col_jp = st.columns(3)

        with col_eu:
            eu_status = st.selectbox(
                "EU compliance",
                ["", "OK", "NOK", "NA"],
                index=["", "OK", "NOK", "NA"].index(req.compliance_eu or ""),
            )

        with col_in:
            in_status = st.selectbox(
                "India compliance",
                ["", "OK", "NOK", "NA"],
                index=["", "OK", "NOK", "NA"].index(req.compliance_india or ""),
            )

        with col_jp:
            jp_status = st.selectbox(
                "Japan compliance",
                ["", "OK", "NOK", "NA"],
                index=["", "OK", "NOK", "NA"].index(req.compliance_japan or ""),
            )

        if st.button("💾 Save compliance for this requirement"):
            store.update_compliance(req.id, eu_status or None, in_status or None, jp_status or None)
            st.success("Compliance updated ✔")
            # force refresh of local object
            all_reqs = store.list_requirements()

        # --- Compliance matrix table ---
        st.markdown("<div class='section-title'>Compliance matrix (R67 vs markets)</div>", unsafe_allow_html=True)

        rows = []
        for r in all_reqs:
            rows.append(
                {
                    "Requirement": r.id,
                    "Engineering formulation": r.text_engineering,
                    "EU": r.compliance_eu or "",
                    "India": r.compliance_india or "",
                    "Japan": r.compliance_japan or "",
                }
            )

        df_comp = pd.DataFrame(rows)
        st.dataframe(df_comp, use_container_width=True)

        # --- KPIs per market ---
        def compute_rate(series):
            vals = [v for v in series if v in ("OK", "NOK")]
            if not vals:
                return 0.0, 0, 0
            ok = sum(1 for v in vals if v == "OK")
            nok = sum(1 for v in vals if v == "NOK")
            rate = 100.0 * ok / max(1, (ok + nok))
            return round(rate, 1), ok, nok

        st.markdown("<div class='section-title'>Market-level KPIs</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        eu_rate, eu_ok, eu_nok = compute_rate(df_comp["EU"])
        in_rate, in_ok, in_nok = compute_rate(df_comp["India"])
        jp_rate, jp_ok, jp_nok = compute_rate(df_comp["Japan"])

        with col1:
            st.markdown("*EU*")
            st.metric("Compliance rate", f"{eu_rate} %")
            st.write(f"OK: {eu_ok}  •  NOK: {eu_nok}")

        with col2:
            st.markdown("*India*")
            st.metric("Compliance rate", f"{in_rate} %")
            st.write(f"OK: {in_ok}  •  NOK: {in_nok}")

        with col3:
            st.markdown("*Japan*")
            st.metric("Compliance rate", f"{jp_rate} %")
            st.write(f"OK: {jp_ok}  •  NOK: {jp_nok}")

        # --- Simple bar chart for visual comparison ---
        st.markdown("#### Compliance rate per market")
        kpi_df = pd.DataFrame(
            {
                "Market": ["EU", "India", "Japan"],
                "Compliance rate (%)": [eu_rate, in_rate, jp_rate],
            }
        ).set_index("Market")
        st.bar_chart(kpi_df)