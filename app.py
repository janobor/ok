import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Logistics Optimizer", layout="wide")

st.title("📦 Logistics Optimizer Dashboard")

# ---------------------------
# DATA
# ---------------------------
data = {
    "Product": ["A", "B", "C"],
    "Annual_Demand": [1200, 800, 1500],
    "Order_Cost": [100, 120, 90],
    "Holding_Cost": [5, 6, 4],
    "Unit_Price": [20, 35, 15]
}

df = pd.DataFrame(data)

# ---------------------------
# SIDEBAR
# ---------------------------
st.sidebar.header("⚙️ Parametry logistyczne")

transport_cost_per_km = st.sidebar.slider("Koszt transportu (PLN / km)", 1.0, 10.0, 3.5)
distance = st.sidebar.slider("Odległość magazyn → klient (km)", 10, 500, 120)

# ---------------------------
# INVENTORY TABLE
# ---------------------------
st.subheader("📊 Dane magazynowe")
edited_df = st.data_editor(df, num_rows="dynamic")

# ---------------------------
# EOQ CALCULATION
# ---------------------------
def calculate_eoq(demand, order_cost, holding_cost):
    return np.sqrt((2 * demand * order_cost) / holding_cost)

edited_df["EOQ"] = edited_df.apply(
    lambda x: calculate_eoq(
        x["Annual_Demand"],
        x["Order_Cost"],
        x["Holding_Cost"]
    ),
    axis=1
)

# ---------------------------
# TRANSPORT COST
# ---------------------------
edited_df["Transport_Cost"] = (
    distance * transport_cost_per_km
)

edited_df["Total_Annual_Cost"] = (
    (edited_df["Annual_Demand"] / edited_df["EOQ"]) * edited_df["Order_Cost"]
    + (edited_df["EOQ"] / 2) * edited_df["Holding_Cost"]
    + edited_df["Transport_Cost"]
)

# ---------------------------
# RESULTS
# ---------------------------
st.subheader("📈 Wyniki optymalizacji")

st.dataframe(
    edited_df.style.format({
        "EOQ": "{:.0f}",
        "Transport_Cost": "{:.2f}",
        "Total_Annual_Cost": "{:.2f}"
    })
)

# ---------------------------
# CHARTS
# ---------------------------
st.subheader("📉 Koszt całkowity wg produktu")

st.bar_chart(
    edited_df.set_index("Product")["Total_Annual_Cost"]
)

# ---------------------------
# SUMMARY
# ---------------------------
best_product = edited_df.loc[
    edited_df["Total_Annual_Cost"].idxmin(), "Product"
]

st.success(f"✅ Najbardziej opłacalny produkt logistycznie: **{best_product}**")
