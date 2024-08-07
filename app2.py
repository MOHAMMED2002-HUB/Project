import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Générer des données normales
data = np.random.normal(size=100)
data = pd.DataFrame(data, columns=["distnorm"])

# Afficher les premières lignes du DataFrame
st.write(data.head())

# Créer un histogramme
fig, ax = plt.subplots()
ax.hist(data["distnorm"])

# Afficher le graphique avec Streamlit
st.pyplot(fig)
