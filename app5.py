import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Fonction pour calculer les KPI
def calculate_kpis(data):
    total_time = data['Temps de Production'].sum()
    total_production = data['Nombre de Produits Fabriqués'].sum()
    total_downtime = data['Temps d\'Arrêt'].sum()
    total_failures = data['Nombre de Pannes'].sum()

    if total_time > 0:
        production_rate = (total_production / total_time) * 100
        mtbf = total_time / total_failures if total_failures > 0 else 0
        mttr = total_downtime / total_failures if total_failures > 0 else 0
    else:
        production_rate = mtbf = mttr = 0

    return production_rate, mtbf, mttr

# Interface utilisateur
st.title("Tableau de Bord de Performance en Temps Réel")

# Formulaire de Saisie des Données
st.header("Entrée des Données")
st.write("Entrez les informations de production et de maintenance.")

# Champs de saisie
temps_production = st.number_input("Temps de Production (en heures)", min_value=0.0)
nombre_produits = st.number_input("Nombre de Produits Fabriqués", min_value=0)
temps_arret = st.number_input("Temps d'Arrêt (en heures)", min_value=0.0)
nombre_pannes = st.number_input("Nombre de Pannes", min_value=0)

# Ajouter des données au DataFrame
data = pd.DataFrame({
    'Temps de Production': [temps_production],
    'Nombre de Produits Fabriqués': [nombre_produits],
    'Temps d\'Arrêt': [temps_arret],
    'Nombre de Pannes': [nombre_pannes]
})

# Calcul des KPI
production_rate, mtbf, mttr = calculate_kpis(data)

# Affichage des résultats
st.header("Résultats de Performance")
st.write(f"**Taux de Production:** {production_rate:.2f}%")
st.write(f"**Temps Moyen Entre Pannes (MTBF):** {mtbf:.2f} heures")
st.write(f"**Temps Moyen de Réparation (MTTR):** {mttr:.2f} heures")

# Objectifs pour les KPI
objective_production_rate = 100
objective_mtbf = temps_production
objective_mttr = 10  # Exemple d'objectif pour le MTTR

# Graphique Thermomètre pour le Taux de Production
st.header("Graphique Thermomètre pour le Taux de Production")
fig_production_rate = go.Figure()
fig_production_rate.add_trace(go.Indicator(
    mode="gauge+number",
    value=production_rate,
    gauge=dict(
        axis=dict(range=[0, objective_production_rate]),
        bar=dict(color="lightblue"),
        steps=[
            {"range": [0, production_rate], "color": "green"},
            {"range": [production_rate, objective_production_rate], "color": "red"}
        ],
        threshold=dict(
            line=dict(color="red", width=4),
            thickness=0.75,
            value=production_rate
        )
    ),
    title={"text": "Taux de Production (%)"}
))
st.plotly_chart(fig_production_rate)

# Graphique Thermomètre pour MTBF
st.header("Graphique Thermomètre pour MTBF")
fig_mtbf = go.Figure()
fig_mtbf.add_trace(go.Indicator(
    mode="gauge+number",
    value=mtbf,
    gauge=dict(
        axis=dict(range=[0, objective_mtbf]),
        bar=dict(color="lightblue"),
        steps=[
            {"range": [0, mtbf], "color": "green"},
            {"range": [mtbf, objective_mtbf], "color": "red"}
        ],
        threshold=dict(
            line=dict(color="red", width=4),
            thickness=0.75,
            value=mtbf
        )
    ),
    title={"text": "Temps Moyen Entre Pannes (MTBF) (heures)"}
))
st.plotly_chart(fig_mtbf)

# Graphique Thermomètre pour MTTR
st.header("Graphique Thermomètre pour MTTR")
fig_mttr = go.Figure()
fig_mttr.add_trace(go.Indicator(
    mode="gauge+number",
    value=mttr,
    gauge=dict(
        axis=dict(range=[0, objective_mttr]),
        bar=dict(color="lightblue"),
        steps=[
            {"range": [0, mttr], "color": "green"},
            {"range": [mttr, objective_mttr], "color": "red"}
        ],
        threshold=dict(
            line=dict(color="red", width=4),
            thickness=0.75,
            value=mttr
        )
    ),
    title={"text": "Temps Moyen de Réparation (MTTR) (heures)"}
))
st.plotly_chart(fig_mttr)

# Interface pour Prévisions (simple exemple)
st.header("Prévisions")
st.write("Entrez des prévisions pour estimer les besoins futurs en maintenance.")
temps_production_future = st.number_input("Temps de Production Futur (en heures)", min_value=0.0)
temps_arret_future = st.number_input("Temps d'Arrêt Futur (en heures)", min_value=0.0)

if temps_production_future > 0:
    future_production_rate = (temps_production_future / (temps_production_future + temps_arret_future)) * 100
    st.write(f"**Prévision de Taux de Production Futur:** {future_production_rate:.2f}%")
