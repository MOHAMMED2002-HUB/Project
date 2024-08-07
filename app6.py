import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Data structures to store inventory data
stock_data = []

# Functions to manage stock
def add_stock(item, quantity, cost, date):
    stock_data.append({'Item': item, 'Quantity': quantity, 'Cost': cost, 'Date': date})

def remove_stock(item, quantity, date):
    global stock_data
    for record in stock_data:
        if record['Item'] == item and record['Quantity'] >= quantity:
            record['Quantity'] -= quantity
            if record['Quantity'] == 0:
                stock_data.remove(record)
            break

# Functions to calculate stock valuation
def calculate_fifo():
    fifo_value = 0
    for record in stock_data:
        fifo_value += record['Quantity'] * record['Cost']
    return fifo_value

def calculate_lifo():
    lifo_value = 0
    for record in reversed(stock_data):
        lifo_value += record['Quantity'] * record['Cost']
    return lifo_value

def calculate_cump():
    total_quantity = sum([record['Quantity'] for record in stock_data])
    total_cost = sum([record['Quantity'] * record['Cost'] for record in stock_data])
    if total_quantity == 0:
        return 0
    cump_value = total_cost / total_quantity
    return cump_value * total_quantity

# Streamlit interface
st.title("Gestion de Stock en Temps Réel")

# Add stock form
st.header("Ajouter un article au stock")
item = st.text_input("Nom de l'article")
quantity = st.number_input("Quantité", min_value=0)
cost = st.number_input("Coût unitaire", min_value=0.0)
date = st.date_input("Date d'ajout")
if st.button("Ajouter"):
    add_stock(item, quantity, cost, date)
    st.success(f"Article {item} ajouté au stock.")

# Remove stock form
st.header("Sortir un article du stock")
item = st.text_input("Nom de l'article à sortir")
quantity = st.number_input("Quantité à sortir", min_value=0)
date = st.date_input("Date de sortie")
if st.button("Sortir"):
    remove_stock(item, quantity, date)
    st.success(f"Article {item} sorti du stock.")

# Display stock valuation
st.header("Valorisation du stock")
fifo_value = calculate_fifo()
lifo_value = calculate_lifo()
cump_value = calculate_cump()

st.write(f"Valorisation FIFO: {fifo_value}")
st.write(f"Valorisation LIFO: {lifo_value}")
st.write(f"Valorisation CUMP: {cump_value}")

# Display stock data
st.header("Données de stock")
st.write(pd.DataFrame(stock_data))
