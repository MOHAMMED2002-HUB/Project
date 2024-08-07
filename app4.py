import streamlit as st 
import pandas as pd 
import numpy as np 

st.title("mohammed")
st.subheader("auteur : mohammed")
st.markdown("***cette application est benefique***")

randomdata = np.random.normal(size = 100)
st.line_chart(randomdata)
