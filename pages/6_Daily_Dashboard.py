import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date
from src.report import get_orders

st.set_page_config(page_title="Daily Dashboard", layout="wide")

if "orders_data" in st.session_state:
    del st.session_state["orders_data"]

# Filters
st.sidebar.header("🔎 Filters")
filtered_date = st.sidebar.date_input("Date", date.today())
if filtered_date:
    orders_data = get_orders(dt=filtered_date)


# KPIs
def kpi_metrics():
    total_orders = orders_data["id"].nunique()
    total_quantity = orders_data["quantity"].sum()
    total_revenue = orders_data["paid_amount"].sum()
    total_delivery_charges = orders_data["delivery_charges"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🧾 Orders", total_orders)
    col2.metric("📦 Quantity", total_quantity)
    col3.metric("💰 Revenue", f"{total_revenue:,}")
    col4.metric("🚚 Delivery Charges", f"{total_delivery_charges:,}")
    st.divider()


# Quantity & Revenue by Stock Category
def quantity_and_revenue_by_stock_category():
    agg_stock_category = orders_data.groupby(["stock_category_id", "stock_category_name"]).agg({
        "quantity": "sum",
        "amount": "sum"
    }).reset_index()
    agg_stock_category.columns = ["Category ID", "Category Name", "Quantity", "Amount"]

    col1, col2 = st.columns(2)
    with col1:  
        # Quantity - Pie/Donut Chart
        st.markdown("📦 Quantity by Stock Category")
        pie = alt.Chart(agg_stock_category) \
            .mark_arc(innerRadius=40) \
            .encode(
                theta="Quantity",
                color="Category Name",
                tooltip=["Category Name", "Quantity"]
            )
        st.altair_chart(pie, use_container_width=True)
    with col2:
        pass


if orders_data.shape[0]:
    st.title("📊 Daily Dashboard")
    st.markdown(f"### Date: `{filtered_date}`")

    kpi_metrics()
    quantity_and_revenue_by_stock_category()
else:
    st.info("No data available 📭")
