import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Application de distribution normale")
st.subheader("Auteur :mohammed")
st.write(
    ("cette application montre l'histogramme d'une disttribution normame")
)

# Générer des données normales
data = np.random.normal(size=100)
data = pd.DataFrame(data, columns=["distnorm"])

# Afficher les premières lignes du DataFrame
st.write(data.head())

# Demander à l'utilisateur de spécifier le nombre de bins
num_bins = st.number_input('Select number of bins', min_value=5, max_value=50, value=20)

# Créer un histogramme avec le nombre de bins spécifié par l'utilisateur
fig, ax = plt.subplots()
ax.hist(data["distnorm"], bins=num_bins)  # Utiliser le nombre de bins spécifié par l'utilisateur

# Afficher le graphique avec Streamlit
st.pyplot(fig)
titre = st.text_input(label="entrer")
plt.title(titre)

st.pyplot(fig)
