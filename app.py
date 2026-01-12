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

# Sprawdzenie czy zmienne istnieją
if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("❌ SUPABASE_URL lub SUPABASE_KEY nie zostały ustawione w Secrets / Environment Variables!")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------
# FUNKCJE
# -----------------------
def load_inventory():
    """Pobiera dane z tabeli inventory w Supabase"""
    response = supabase.table("inventory").select("*").execute()
    if response.error:
        st.error(f"Błąd pobierania danych: {response.error.message}")
        return pd.DataFrame()
    return pd.DataFrame(response.data)

def calculate_eoq(demand, order_cost, holding_cost):
    """Oblicza EOQ dla pojedynczego produktu"""
    try:
        return np.sqrt((2 * demand * order_cost) / holding_cost)
    except Exception:
        return np.nan

# -----------------------
# UI
# -----------------------
st.subheader("📊 Dane z Supabase")

# Odświeżanie danych przy każdym wczytaniu lub przycisku
if st.button("🔄 Odśwież dane"):
    df = load_inventory()
else:
    df = load_inventory()

if df.empty:
    st.warning("Tabela inventory jest pusta lub RLS nie pozwala na SELECT.")
else:
    st.dataframe(df)

    # -----------------------
    # EOQ
    # -----------------------
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
    # EXPORT DANYCH
    # -----------------------
    st.subheader("⬇️ Eksport danych")

    # CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Pobierz CSV",
        csv,
        "inventory.csv",
        "text/csv"
    )

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
