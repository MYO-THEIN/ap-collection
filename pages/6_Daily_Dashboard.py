import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date
from src.report import get_orders

st.set_page_config(layout="wide")

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
    total_revenue = orders_data.groupby("id")["paid_amount"].first().sum()
    total_delivery_charges = orders_data.groupby("id")["delivery_charges"].first().sum()

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
    agg_stock_category.columns = ["Stock Category ID", "Stock Category", "Quantity", "Amount"]

    col1, col2 = st.columns(2)
    with col1:  
        # Quantity - Pie Chart
        st.markdown("📦 Quantity by Stock Category")
        pie_quantity_by_stock_category = alt.Chart(agg_stock_category) \
            .mark_arc(innerRadius=40) \
            .encode(
                theta="Quantity",
                color="Stock Category",
                tooltip=[
                    alt.Tooltip("Stock Category", title="Stock Category"),
                    alt.Tooltip("Quantity", title="Quantity")
                ]
            )
        st.altair_chart(pie_quantity_by_stock_category, use_container_width=True)
    
    with col2:
        # Revenue - Bar Chart
        st.markdown("💰 Revenue by Stock Category")
        bar_revenue_by_stock_category = alt.Chart(agg_stock_category) \
            .mark_bar() \
            .encode(
                x=alt.X("Stock Category", sort="-y", title="Stock Category"),
                y=alt.Y("Amount", title="Revenue"),
                tooltip=[
                    alt.Tooltip("Stock Category", title="Stock Category"),
                    alt.Tooltip("Amount", title="Revenue", format=",.0f")
                ]
            )
        st.altair_chart(bar_revenue_by_stock_category, use_container_width=True)

    st.divider()


# Revenue Breakdown
def revenue_breakdown():
    col1, col2, col3 = st.columns(3)
    with col1:
        # By Payment Type - Pie Chart
        agg_payment_type = orders_data.drop_duplicates(subset=["id"]).groupby(["payment_type_id", "payment_type_name"]).agg({
            "paid_amount": "sum"
        }).reset_index()
        agg_payment_type.columns = ["Payment Type ID", "Payment Type", "Paid Amount"]

        st.markdown("💳 Revenue by Payment Type")
        pie_revenue_by_payment_type = alt.Chart(agg_payment_type) \
            .mark_arc(innerRadius=40) \
            .encode(
                theta="Paid Amount",
                color="Payment Type",
                tooltip=[
                    alt.Tooltip("Payment Type", title="Payment Type"),
                    alt.Tooltip("Paid Amount", title="Revenue", format=",.0f")
                ]
            )
        st.altair_chart(pie_revenue_by_payment_type, use_container_width=True)

    with col2:
        agg_city_state_region = orders_data.groupby(["customer_city", "customer_state_region"]).agg({
            "quantity": "sum",
            "amount": "sum"
        }).reset_index()
        agg_city_state_region.columns = ["City", "State_Region", "Quantity", "Amount"]

        # By City
        st.markdown("🏙️ By City")
        bar_by_city = alt.Chart(agg_city_state_region) \
            .transform_fold(fold=["Amount", "Quantity"], as_=["Amount", "Quantity"]) \
            .mark_bar() \
            .encode(
                x=alt.X("City:N", title="City"),
                y=alt.Y("Quantity:Q"),
                color="Amount:N",
                column="Amount:N",
                tooltip=[
                    alt.Tooltip("City:N"),
                    alt.Tooltip("Amount:N"),
                    alt.Tooltip("Quantity:Q")
                ]
            )
        st.altair_chart(bar_by_city, use_container_width=True)

    with col3:
        pass

    st.divider()


if orders_data.shape[0]:
    st.title("📊 Daily Dashboard")
    st.markdown(f"### Date: `{filtered_date}`")

    kpi_metrics()
    quantity_and_revenue_by_stock_category()
    revenue_breakdown()
else:
    st.info("No data available 📭")
