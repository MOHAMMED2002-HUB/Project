import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np

# Fonction pour calculer les KPI
def calculate_kpis(data, max_capacity):
    total_time = data['Temps de Production'].sum()
    total_production = data['Nombre de Produits Fabriqués'].sum()
    total_downtime = data['Temps d\'Arrêt'].sum()
    total_failures = data['Nombre de Pannes'].sum()

    if total_time > 0 and max_capacity > 0:
        production_rate = (total_production / total_time) / max_capacity * 100
        mtbf = total_time / total_failures if total_failures > 0 else 0
        mttr = total_downtime / total_failures if total_failures > 0 else 0
    else:
        production_rate = mtbf = mttr = 0

    return production_rate, mtbf, mttr

# Fonction pour faire une prévision
def make_forecast(data):
    model = LinearRegression()
    X = np.array(data.index).reshape(-1, 1)  # Utilisation de l'index comme variable indépendante
    y = data['Nombre de Produits Fabriqués']  # Variable dépendante
    model.fit(X, y)  # Entraîner le modèle
    future_index = np.array([[len(data)]])  # Index pour la prévision future
    forecast = model.predict(future_index)  # Faire la prévision
    return forecast[0]

# Interface utilisateur
st.title("Application de suivi de performance et d'analyse prédictive")

st.markdown("""
### Cette application sert à suivre la performance de production et à effectuer des analyses prédictives.
Entrez les informations ci-dessous pour calculer les KPI et visualiser les résultats.
""")

# Champs de saisie
temps_production = st.number_input("Temps de Production (en heures)", min_value=0.0)
nombre_produits = st.number_input("Nombre de Produits Fabriqués", min_value=0)
temps_arret = st.number_input("Temps d'Arrêt (en heures)", min_value=0.0)
nombre_pannes = st.number_input("Nombre de Pannes", min_value=0)
max_capacity = st.number_input("Capacité de Production Maximale", min_value=0.0)

# Vérifier si tous les champs ont été remplis
if temps_production > 0 and nombre_produits > 0 and temps_arret > 0 and nombre_pannes > 0 and max_capacity > 0:
    # Ajouter des données au DataFrame
    data = pd.DataFrame({
        'Temps de Production': [temps_production],
        'Nombre de Produits Fabriqués': [nombre_produits],
        'Temps d\'Arrêt': [temps_arret],
        'Nombre de Pannes': [nombre_pannes]
    })

    # Calcul des KPI
    production_rate, mtbf, mttr = calculate_kpis(data, max_capacity)

    # Affichage des résultats
    st.header("Résultats de Performance")
    st.write(f"**Taux de Production:** {production_rate:.2f}%")
    st.write(f"**Temps Moyen Entre Pannes (MTBF):** {mtbf:.2f} heures")
    st.write(f"**Temps Moyen de Réparation (MTTR):** {mttr:.2f} heures")

    # Objectifs pour les KPI
    objective_production_rate = 100
    objective_mtbf = temps_production
    objective_mttr = 2  # Objectif pour le MTTR

    # Graphique Thermomètre pour le Taux de Production
    st.header("Thermometer Chart for Production Rate")
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
        title={"text": "Production rate (%)"}
    ))
    st.plotly_chart(fig_production_rate)

    # Graphique Thermomètre pour MTBF
    st.header("Thermometer Chart for the MTBF")
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
        title={"text": "Mean time between failure"}
    ))
    st.plotly_chart(fig_mtbf)

    # Graphique Thermomètre pour MTTR
    st.header("Thermometer Chart for the MTTR")
    fig_mttr = go.Figure()
    fig_mttr.add_trace(go.Indicator(
        mode="gauge+number",
        value=mttr,
        gauge=dict(
            axis=dict(range=[0, objective_mttr]),
            bar=dict(color="lightblue"),
            steps=[
                {"range": [0, mtbf], "color": "green"},
                {"range": [mttr, 2], "color": "red"}
            ],
            threshold=dict(
                line=dict(color="red", width=4),
                thickness=0.75,
                value=mttr
            )
        ),
        title={"text": "Mean time to repair"}
    ))
    st.plotly_chart(fig_mttr)
else:
    st.write("Please complete all fields to view results and graphs.")

# Ajouter un bouton pour télécharger un fichier Excel
uploaded_file = st.file_uploader("Choose an Excel file to make a forecast", type="xlsx")

# Bouton pour faire la prévision
if uploaded_file:
    data_forecast = pd.read_excel(uploaded_file)
    if st.button("Predict"):
        forecast = make_forecast(data_forecast)
        st.write(f"The forecast for the number of products produced is: {forecast:.2f}")
