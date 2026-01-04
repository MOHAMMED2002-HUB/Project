import streamlit as st
import pandas as pd
import plotly.express as px
import os

# =========================
# CONFIGURATION PAGE
# =========================
st.set_page_config(
    page_title="Suivi Maintenance & Production",
    layout="wide"
)

st.title("📊 Application de Suivi Maintenance & Production")

# =========================
# FONCTIONS KPI
# =========================
def calculate_kpis(pannes, production, backlog):
    mttr = pannes["Temps_Panne (h)"].mean()
    mtbf = pannes["Temps_Fonctionnement (h)"].mean()
    oee_moyen = production["OEE"].mean() * 100

    dispo_globale = (
        production["Temps_Fonctionnement (h)"].sum()
        / production["Temps_Disponible (h)"].sum()
        * 100
        if production["Temps_Disponible (h)"].sum() > 0 else 0
    )

    backlog_pct = (
        len(backlog) / (len(backlog) + len(pannes)) * 100
        if (len(backlog) + len(pannes)) > 0 else 0
    )

    return mttr, mtbf, oee_moyen, dispo_globale, backlog_pct


# =========================
# MENU LATERAL
# =========================
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Choisir une page",
    [
        "Accueil",
        "KPIs Maintenance",
        "Analyse Pannes",
        "Production & OEE",
        "Backlog",
        "Power BI Connect"
    ]
)

st.sidebar.markdown("---")

# =========================
# IMPORT DES FICHIERS
# =========================
uploaded_pannes = st.sidebar.file_uploader("📂 Pannes.xlsx", type="xlsx")
uploaded_backlog = st.sidebar.file_uploader("📂 Backlog.xlsx", type="xlsx")
uploaded_production = st.sidebar.file_uploader("📂 Production.xlsx", type="xlsx")

if uploaded_pannes and uploaded_backlog and uploaded_production:

    # =========================
    # LECTURE DES DONNÉES
    # =========================
    pannes = pd.read_excel(uploaded_pannes)
    backlog = pd.read_excel(uploaded_backlog)
    production = pd.read_excel(uploaded_production)

    # Dates
    pannes["Date_Début"] = pd.to_datetime(pannes["Date_Début"])
    pannes["Date_Fin"] = pd.to_datetime(pannes["Date_Fin"])
    production["Date"] = pd.to_datetime(production["Date"])

    # =========================
    # CALCUL OEE
    # =========================
    production["Disponibilité"] = production["Temps_Fonctionnement (h)"] / production["Temps_Disponible (h)"]
    production["Qualité"] = production["Quantité_Bonne"] / production["Quantité_Totale"]
    production["OEE"] = production["Disponibilité"] * production["Qualité"]

    # =========================
    # KPI GLOBAUX
    # =========================
    mttr, mtbf, oee_moyen, dispo_globale, backlog_pct = calculate_kpis(
        pannes, production, backlog
    )

    # =========================
    # FILTRES
    # =========================
    st.sidebar.subheader("🔍 Filtres")

    machines = st.sidebar.multiselect(
        "Machines",
        options=pannes["Machine"].unique(),
        default=pannes["Machine"].unique()
    )

    pannes_f = pannes[pannes["Machine"].isin(machines)]
    production_f = production[production["Machine"].isin(machines)]

    # =========================
    # PAGE ACCUEIL
    # =========================
    if page == "Accueil":
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("⚙ MTBF (h)", f"{mtbf:.2f}")
        col2.metric("⏱ MTTR (h)", f"{mttr:.2f}")
        col3.metric("📈 OEE Moyen (%)", f"{oee_moyen:.1f}%")
        col4.metric("📋 Backlog (%)", f"{backlog_pct:.1f}%")

        st.markdown("### Vue globale maintenance & production")

    # =========================
    # KPIs MAINTENANCE
    # =========================
    elif page == "KPIs Maintenance":

        st.subheader("📊 Indicateurs clés")

        col1, col2, col3 = st.columns(3)
        col1.metric("MTBF (h)", f"{mtbf:.2f}")
        col2.metric("MTTR (h)", f"{mttr:.2f}")
        col3.metric("Disponibilité (%)", f"{dispo_globale:.1f}%")

        st.markdown("### Évolution MTBF / MTTR")

        kpi_time = (
            pannes_f
            .groupby(pannes_f["Date_Début"].dt.to_period("M"))
            .agg({
                "Temps_Fonctionnement (h)": "mean",
                "Temps_Panne (h)": "mean"
            })
            .reset_index()
        )

        kpi_time["Date"] = kpi_time["Date_Début"].dt.to_timestamp()

        fig = px.line(
            kpi_time,
            x="Date",
            y=["Temps_Fonctionnement (h)", "Temps_Panne (h)"],
            markers=True
        )

        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # ANALYSE DES PANNES
    # =========================
    elif page == "Analyse Pannes":

        st.subheader("🔧 Pannes par machine")

        panne_machine = pannes_f["Machine"].value_counts().reset_index()
        panne_machine.columns = ["Machine", "Nb_Pannes"]

        fig1 = px.bar(
            panne_machine,
            x="Machine",
            y="Nb_Pannes",
            color="Nb_Pannes"
        )
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("📊 Pareto des causes de pannes")

        if "Cause" in pannes_f.columns:
            cause_count = pannes_f["Cause"].value_counts().reset_index()
            cause_count.columns = ["Cause", "Nb_Pannes"]

            fig2 = px.bar(
                cause_count,
                x="Cause",
                y="Nb_Pannes"
            )
            st.plotly_chart(fig2, use_container_width=True)

    # =========================
    # PRODUCTION & OEE
    # =========================
    elif page == "Production & OEE":

        st.subheader("🏭 OEE par machine")

        oee_machine = (
            production_f
            .groupby("Machine")["OEE"]
            .mean()
            .reset_index()
        )

        fig_oee = px.bar(
            oee_machine,
            x="Machine",
            y="OEE",
            text=oee_machine["OEE"].apply(lambda x: f"{x*100:.1f}%")
        )

        fig_oee.update_traces(textposition="outside")
        st.plotly_chart(fig_oee, use_container_width=True)

        st.subheader("📋 Données de production")
        st.dataframe(production_f)

    # =========================
    # BACKLOG
    # =========================
    elif page == "Backlog":

        st.subheader("📅 Backlog par priorité")

        if "Priorité" in backlog.columns:
            backlog_prio = backlog["Priorité"].value_counts().reset_index()
            backlog_prio.columns = ["Priorité", "Nb_Ordres"]

            fig = px.bar(
                backlog_prio,
                x="Priorité",
                y="Nb_Ordres",
                color="Priorité"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(backlog)

    # =========================
    # POWER BI CONNECT
    # =========================
    elif page == "Power BI Connect":

        st.subheader("🔗 Connexion Power BI")

        export_folder = r"C:\Users\lenovo\Desktop\export_powerbi"
        os.makedirs(export_folder, exist_ok=True)
        csv_path = os.path.join(export_folder, "data_powerbi.csv")

        df_powerbi = pd.concat([
            pannes_f.assign(Source="Pannes"),
            production_f.assign(Source="Production"),
            backlog.assign(Source="Backlog")
        ])

        if st.button("📤 Générer fichier Power BI"):
            df_powerbi.to_csv(csv_path, index=False)
            st.success(f"Fichier généré : {csv_path}")

        st.info("👉 Power BI → Obtenir des données → CSV")

else:
    st.warning("📌 Importez les 3 fichiers Excel pour démarrer")
