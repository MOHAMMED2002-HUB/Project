import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
from fbprophet import Prophet
import sqlite3

# Configuration de la base de données SQLite
conn = sqlite3.connect('data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS production_data (
                id INTEGER PRIMARY KEY,
                temps_production REAL,
                nombre_produits INTEGER,
                temps_arret REAL,
                nombre_pannes INTEGER)''')
conn.commit()

# Fonction pour ajouter des données à la base de données
def add_data(temps_production, nombre_produits, temps_arret, nombre_pannes):
    c.execute("INSERT INTO production_data (temps_production, nombre_produits, temps_arret, nombre_pannes) VALUES (?, ?, ?, ?)",
              (temps_production, nombre_produits, temps_arret, nombre_pannes))
    conn.commit()

# Fonction pour récupérer les données de la base de données
def get_data():
    c.execute("SELECT * FROM production_data")
    data = c.fetchall()
    return pd.DataFrame(data, columns=['id', 'Temps de Production', 'Nombre de Produits Fabriqués', 'Temps d\'Arrêt', 'Nombre de Pannes'])

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

# Fonction de prévision avec Prophet
def make_advanced_forecast(data):
    data['ds'] = data.index
    data['y'] = data['Nombre de Produits Fabriqués']
    model = Prophet()
    model.fit(data)
    future = model.make_future_dataframe(periods=1)
    forecast = model.predict(future)
    return forecast.iloc[-1]['yhat']

# Interface utilisateur
st.title("Application de suivi de performance et d'analyse prédictive")

# Formulaire de Saisie des Données
st.header("Entrez les données")
st.write("Entrez les informations de production et de maintenance.")

# Champs de saisie
temps_production = st.number_input("Temps de Production (en heures)", min_value=0.0)
nombre_produits = st.number_input("Nombre de Produits Fabriqués", min_value=0)
temps_arret = st.number_input("Temps d'Arrêt (en heures)", min_value=0.0)
nombre_pannes = st.number_input("Nombre de Pannes", min_value=0)
max_capacity = st.number_input("Capacité de Production Maximale", min_value=0.0)

# Ajout de données
if st.button("Ajouter"):
    if temps_production > 0 and nombre_produits > 0 and temps_arret > 0 and nombre_pannes > 0 and max_capacity > 0:
        add_data(temps_production, nombre_produits, temps_arret, nombre_pannes)
        st.success("Données ajoutées avec succès!")
    else:
        st.error("Tous les champs doivent être remplis avec des valeurs positives.")

# Affichage des données et calcul des KPI
data = get_data()
if not data.empty:
    st.header("Données de Production")
    st.write(data)

    production_rate, mtbf, mttr = calculate_kpis(data, max_capacity)

    # Affichage des résultats
    st.header("Résultats de Performance")
    st.write(f"**Taux de Production:** {production_rate:.2f}%")
    st.write(f"**Temps Moyen Entre Pannes (MTBF):** {mtbf:.2f} heures")
    st.write(f"**Temps Moyen de Réparation (MTTR):** {mttr:.2f} heures")

    # Objectifs pour les KPI
    objective_production_rate = 100
    objective_mtbf = data['Temps de Production'].max()  # Utilisation du temps de production maximum comme objectif
    objective_mttr = 2  # Objectif pour le MTTR

    # Choisir les couleurs pour les graphiques
    color_choice = st.color_picker("Choisir une couleur pour les graphiques", "#00f900")

    # Graphique Thermomètre pour le Taux de Production
    st.header("Graphique Thermomètre pour le Taux de Production")
    fig_production_rate = go.Figure()
    fig_production_rate.add_trace(go.Indicator(
        mode="gauge+number",
        value=production_rate,
        gauge=dict(
            axis=dict(range=[0, objective_production_rate]),
            bar=dict(color=color_choice),
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
    st.header("Graphique Thermomètre pour le MTBF")
    fig_mtbf = go.Figure()
    fig_mtbf.add_trace(go.Indicator(
        mode="gauge+number",
        value=mtbf,
        gauge=dict(
            axis=dict(range=[0, objective_mtbf]),
            bar=dict(color=color_choice),
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
        title={"text": "Temps Moyen Entre Pannes (MTBF)"}
    ))
    st.plotly_chart(fig_mtbf)

    # Graphique Thermomètre pour MTTR
    st.header("Graphique Thermomètre pour le MTTR")
    fig_mttr = go.Figure()
    fig_mttr.add_trace(go.Indicator(
        mode="gauge+number",
        value=mttr,
        gauge=dict(
            axis=dict(range=[0, objective_mttr]),
            bar=dict(color=color_choice),
            steps=[
                {"range": [0, mttr], "color": "green"},
                {"range": [mttr, 2], "color": "red"}
            ],
            threshold=dict(
                line=dict(color="red", width=4),
                thickness=0.75,
                value=mttr
            )
        ),
        title={"text": "Temps Moyen de Réparation (MTTR)"}
    ))
    st.plotly_chart(fig_mttr)

    # Prévision
    uploaded_file = st.file_uploader("Choisissez un fichier Excel pour faire une prévision", type="xlsx")
    if uploaded_file:
        data_forecast = pd.read_excel(uploaded_file)
        if st.button("Prévoir avec Prophet"):
            forecast = make_advanced_forecast(data_forecast)
            st.write(f"La prévision du nombre de produits fabriqués est: {forecast:.2f}")
else:
    st.write("Aucune donnée disponible. Veuillez ajouter des données pour voir les résultats et les graphiques.")

# Documentation
st.sidebar.header("Documentation")
st.sidebar.write("""
- **Entrée de Données** : Saisissez les données de production et de maintenance.
- **Calcul des KPI** : Cliquez sur "Ajouter" pour calculer et afficher les KPI.
- **Prévisions** : Téléchargez un fichier Excel et cliquez sur "Prévoir" pour obtenir des prévisions.
- **Exportation** : Utilisez les boutons d'exportation pour sauvegarder les données.
""")
