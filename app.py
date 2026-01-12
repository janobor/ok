import streamlit as st
import pandas as pd
import numpy as np
from supabase import create_client
import os
from io import BytesIO

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="Logistics Inventory", layout="wide")
st.title("📦 Inventory – Supabase")

# -----------------------
# POŁĄCZENIE Z SUPABASE
# -----------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ SUPABASE_URL lub SUPABASE_KEY nie zostały ustawione w Secrets / Environment Variables!")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------
# FUNKCJE
# -----------------------
def load_inventory():
    """Pobiera dane z tabeli inventory w Supabase"""
    try:
        response = supabase.table("inventory").select("*").execute()
        df = pd.DataFrame(response.data)
        return df
    except Exception as e:
        st.error(f"Błąd pobierania danych z Supabase: {e}")
        return pd.DataFrame()

def add_product(product, annual_demand, order_cost, holding_cost):
    """Dodaje nowy produkt do tabeli inventory w Supabase"""
    try:
        data = {
            "product": product,
            "annual_demand": annual_demand,
            "order_cost": order_cost,
            "holding_cost": holding_cost
        }
        supabase.table("inventory").insert(data).execute()
        st.success(f"Produkt '{product}' dodany do inventory!")
    except Exception as e:
        st.error(f"Błąd przy dodawaniu produktu: {e}")

def calculate_eoq(demand, order_cost, holding_cost):
    """Oblicza EOQ dla pojedynczego produktu"""
    try:
        return np.sqrt((2 * demand * order_cost) / holding_cost)
    except Exception:
        return np.nan

# -----------------------
# UI - DANE
# -----------------------
st.subheader("📊 Dane z Supabase")

if st.button("🔄 Odśwież dane"):
    df = load_inventory()
else:
    df = load_inventory()

if df.empty:
    st.warning("Tabela inventory jest pusta lub RLS nie pozwala na SELECT.")
else:
    st.dataframe(df)

    # EOQ
    df["EOQ"] = df.apply(
        lambda x: calculate_eoq(
            x.get("annual_demand", 0),
            x.get("order_cost", 0),
            x.get("holding_cost", 0)
        ),
        axis=1
    )

    st.subheader("📈 EOQ")
    st.dataframe(df[["product", "EOQ"]])

    # -----------------------
    # FORMULARZ DODAWANIA PRODUKTU
    # -----------------------
    st.subheader("➕ Dodaj nowy produkt")
    with st.form(key="add_product_form"):
        product_name = st.text_input("Nazwa produktu")
        annual_demand = st.number_input("Roczny popyt", min_value=0, value=0)
        order_cost = st.number_input("Koszt zamówienia", min_value=0.0, value=0.0, step=0.01)
        holding_cost = st.number_input("Koszt magazynowania", min_value=0.0, value=0.0, step=0.01)
        submit_button = st.form_submit_button("Dodaj produkt")

        if submit_button:
            if product_name.strip() == "":
                st.warning("Podaj nazwę produktu!")
            else:
                add_product(product_name, annual_demand, order_cost, holding_cost)
                df = load_inventory()  # odświeżenie tabeli po dodaniu

    # -----------------------
    # EXPORT DANYCH
    # -----------------------
    st.subheader("⬇️ Eksport danych")
    # CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Pobierz CSV", csv, "inventory.csv", "text/csv")

    # Excel
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False)
    st.download_button(
        "📥 Pobierz Excel",
        buffer.getvalue(),
        "inventory.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
