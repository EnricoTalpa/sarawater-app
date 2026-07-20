import datetime
import io

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

import sarawater.scenarios as sc
import sarawater.reach as rch

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SARAwater – Analisi scenari idrici",
    page_icon="💧",
    layout="wide",
)

st.title("💧 SARAwater – Analisi scenari di astrazione idrica")
st.caption("Scenario-based Alteration of Rivers subject to water Abstraction")

# ── Helpers ────────────────────────────────────────────────────────────────────

MONTH_NAMES = [
    "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
    "Lug", "Ago", "Set", "Ott", "Nov", "Dic",
]


def generate_synthetic_flow(n_years: int, q_mean: float, q_amplitude: float, seed: int = 42) -> tuple:
    """Sinusoidal seasonal flow with random noise."""
    rng = np.random.default_rng(seed)
    start = datetime.datetime(2020, 1, 1)
    dates = [start + datetime.timedelta(days=i) for i in range(365 * n_years)]
    t = np.arange(len(dates))
    seasonal = q_mean + q_amplitude * np.sin(2 * np.pi * t / 365 - np.pi / 2)
    noise = rng.normal(0, q_mean * 0.1, len(dates))
    Qnat = np.clip(seasonal + noise, 0.1, None)
    return dates, Qnat


def build_reach(cfg: dict) -> rch.Reach:
    dates, Qnat = generate_synthetic_flow(
        cfg["n_years"], cfg["q_mean"], cfg["q_amplitude"]
    )
    return rch.Reach(cfg["name"], dates, Qnat, cfg["qabs_max"])


def add_scenario(reach: rch.Reach, s: dict):
    if s["type"] == "Costante (ConstScenario)":
        scenario = sc.ConstScenario(
            s["name"], s["description"], reach, s["qreq_months"]
        )
    else:
        scenario = sc.PropScenario(
            s["name"],
            s["description"],
            reach,
            Qbase=s["qbase"],
            c_Qin=s["c_qin"],
            Qreq_min=s["qreq_min"],
            Qreq_max=s["qreq_max"],
        )
    reach.add_scenario(scenario)
    scenario.compute_Qrel()
    scenario.compute_natural_abstracted_volumes()
    scenario.compute_IHA_index(index_metric="IARI")
    return scenario


# ── Sidebar – reach configuration ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configurazione Reach")

    reach_name = st.text_input("Nome del tratto", value="Tratto di esempio")
    q_mean = st.number_input("Portata naturale media (m³/s)", min_value=1.0, max_value=500.0, value=30.0, step=1.0)
    q_amplitude = st.number_input("Ampiezza stagionale (m³/s)", min_value=0.0, max_value=200.0, value=20.0, step=1.0)
    n_years = st.slider("Anni di simulazione", min_value=1, max_value=10, value=3)
    qabs_max = st.number_input("Qabs_max – astrazione massima (m³/s)", min_value=0.1, max_value=100.0, value=10.0, step=0.5)

    st.divider()
    st.header("➕ Aggiungi scenario")

    if "scenarios" not in st.session_state:
        st.session_state.scenarios = []

    with st.form("scenario_form", clear_on_submit=True):
        s_name = st.text_input("Nome scenario", value=f"Scenario {len(st.session_state.scenarios) + 1}")
        s_desc = st.text_input("Descrizione", value="")
        s_type = st.selectbox("Tipo", ["Costante (ConstScenario)", "Proporzionale (PropScenario)"])

        if s_type == "Costante (ConstScenario)":
            st.markdown("**Portate mensili richieste (m³/s)**")
            cols = st.columns(4)
            qreq = []
            for i, mname in enumerate(MONTH_NAMES):
                with cols[i % 4]:
                    qreq.append(st.number_input(mname, min_value=0.0, max_value=float(qabs_max), value=5.0, step=0.5, key=f"m{i}"))
        else:
            qbase  = st.number_input("Qbase (m³/s)", min_value=0.0, value=3.0, step=0.5)
            c_qin  = st.number_input("c_Qin (coefficiente proporzionale)", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
            qreq_min = st.number_input("Qreq_min (m³/s)", min_value=0.0, value=2.0, step=0.5)
            qreq_max = st.number_input("Qreq_max (m³/s)", min_value=0.0, value=15.0, step=0.5)

        submitted = st.form_submit_button("Aggiungi scenario")
        if submitted:
            entry = {"name": s_name, "description": s_desc, "type": s_type}
            if s_type == "Costante (ConstScenario)":
                entry["qreq_months"] = qreq
            else:
                entry.update({"qbase": qbase, "c_qin": c_qin, "qreq_min": qreq_min, "qreq_max": qreq_max})
            st.session_state.scenarios.append(entry)
            st.success(f"Scenario '{s_name}' aggiunto.")

    if st.session_state.scenarios:
        if st.button("🗑️ Rimuovi tutti gli scenari"):
            st.session_state.scenarios = []
            st.rerun()

# ── Build reach & scenarios ────────────────────────────────────────────────────
reach_cfg = {
    "name": reach_name,
    "q_mean": q_mean,
    "q_amplitude": q_amplitude,
    "n_years": n_years,
    "qabs_max": qabs_max,
}

reach = build_reach(reach_cfg)
built_scenarios = []
for s in st.session_state.scenarios:
    built_scenarios.append(add_scenario(reach, s))

# ── Main area ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Portate", "📊 Scenari", "🔬 Indici IHA", "📥 Export"])

# ── Tab 1: Portate ─────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Portate naturali e rilasciate")

    dates_arr = np.array(reach.dates)
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(dates_arr, reach.Qnat, color="steelblue", linewidth=0.8, label="Qnat (naturale)")

    if built_scenarios:
        colors = plt.cm.tab10.colors
        for i, scenario in enumerate(built_scenarios):
            ax.plot(dates_arr, scenario.Qrel, linewidth=0.8,
                    color=colors[(i + 1) % len(colors)], label=scenario.name)
    else:
        st.info("Aggiungi almeno uno scenario dalla sidebar per visualizzare le portate rilasciate.")

    ax.set_xlabel("Data")
    ax.set_ylabel("Portata (m³/s)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # Stats table
    st.subheader("Statistiche di base")
    stats = {
        "Serie": ["Qnat (naturale)"] + [s.name for s in built_scenarios],
        "Media (m³/s)": [np.mean(reach.Qnat)] + [np.mean(s.Qrel) for s in built_scenarios],
        "Min (m³/s)": [np.min(reach.Qnat)] + [np.min(s.Qrel) for s in built_scenarios],
        "Max (m³/s)": [np.max(reach.Qnat)] + [np.max(s.Qrel) for s in built_scenarios],
    }
    st.dataframe(pd.DataFrame(stats).set_index("Serie").round(2), use_container_width=True)

# ── Tab 2: Scenari ─────────────────────────────────────────────────────────────
with tab2:
    if not built_scenarios:
        st.info("Aggiungi almeno uno scenario dalla sidebar.")
    else:
        st.subheader("Riepilogo scenari")
        summary_df = reach.export_scenarios_summary()
        core_cols = [c for c in summary_df.columns if not c.startswith("monthly_abs")]
        st.dataframe(summary_df[core_cols], use_container_width=True)

        st.subheader("Volumi mensili astratti medi (m³)")
        month_data = {}
        for scenario in built_scenarios:
            if hasattr(scenario, "monthly_abs_volumes"):
                month_data[scenario.name] = scenario.monthly_abs_volumes
        if month_data:
            month_df = pd.DataFrame(month_data, index=MONTH_NAMES)
            fig2, ax2 = plt.subplots(figsize=(10, 4))
            month_df.plot(kind="bar", ax=ax2, colormap="tab10")
            ax2.set_xlabel("Mese")
            ax2.set_ylabel("Volume astratto medio (m³)")
            ax2.set_xticklabels(MONTH_NAMES, rotation=45)
            ax2.legend(fontsize=8)
            ax2.grid(True, axis="y", alpha=0.3)
            fig2.tight_layout()
            st.pyplot(fig2)
            plt.close(fig2)

# ── Tab 3: Indici IHA ──────────────────────────────────────────────────────────
with tab3:
    if not built_scenarios:
        st.info("Aggiungi almeno uno scenario dalla sidebar.")
    else:
        st.subheader("Indici IARI per scenario")
        st.caption("IARI = Índice de Alteración del Régimen de Caudales (0 = nessuna alterazione, 1 = alterazione massima)")

        iari_rows = []
        for scenario in built_scenarios:
            if hasattr(scenario, "IARI"):
                row = {"Scenario": scenario.name,
                       "IARI aggregato": round(np.mean(scenario.IARI["aggregated"]), 4)}
                for grp, vals in scenario.IARI["groups"].items():
                    row[grp] = round(np.mean(vals), 4)
                iari_rows.append(row)

        if iari_rows:
            iari_df = pd.DataFrame(iari_rows).set_index("Scenario")
            st.dataframe(iari_df, use_container_width=True)

            # Bar chart
            fig3, ax3 = plt.subplots(figsize=(8, 4))
            iari_df.plot(kind="bar", ax=ax3, colormap="Set2")
            ax3.set_ylabel("IARI")
            ax3.set_ylim(0, 1)
            ax3.axhline(0.5, color="red", linestyle="--", linewidth=0.8, label="Soglia 0.5")
            ax3.legend(fontsize=7, loc="upper right")
            ax3.set_xticklabels(iari_df.index, rotation=20, ha="right")
            ax3.grid(True, axis="y", alpha=0.3)
            fig3.tight_layout()
            st.pyplot(fig3)
            plt.close(fig3)

# ── Tab 4: Export ──────────────────────────────────────────────────────────────
with tab4:
    if not built_scenarios:
        st.info("Aggiungi almeno uno scenario dalla sidebar.")
    else:
        st.subheader("Download riepilogo scenari (CSV)")
        summary_df = reach.export_scenarios_summary()
        csv_buffer = io.StringIO()
        summary_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="⬇️ Scarica summary.csv",
            data=csv_buffer.getvalue(),
            file_name="sarawater_summary.csv",
            mime="text/csv",
        )
        st.dataframe(summary_df, use_container_width=True)
