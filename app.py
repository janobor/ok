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

# Połączenie z Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------
# FUNKCJE
# -----------------------
@st.cache_data
def load_inventory():
    response = supabase.table("inventory").select("*").execute()
    return pd.DataFrame(response.data)

def calculate_eoq(demand, order_cost, holding_cost):
    return np.sqrt((2 * demand * order_cost) / holding_cost)

# -----------------------
# LOAD DATA
# -----------------------
df = load_inventory()

if df.empty:
    st.warning("Tabela inventory jest pusta lub RLS nie pozwala na SELECT.")
else:
    st.subheader("📊 Dane z Supabase")
    st.dataframe(df)

    # EOQ
    df["EOQ"] = df.apply(
        lambda x: calculate_eoq(
            x["annual_demand"],
            x["order_cost"],
            x["holding_cost"]
        ),
        axis=1
    )

    st.subheader("📈 EOQ")
    st.dataframe(df[["product", "EOQ"]])

    # -----------------------
    # EXPORT
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
