import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import datetime, date, timedelta
from src.report import get_orders

st.set_page_config(layout="wide")

if "orders_data" in st.session_state:
    del st.session_state["orders_data"]
if "prev_data" in st.session_state:
    del st.session_state["prev_data"]

# Filters
st.sidebar.header("🔎 Filters")
filtered_date = st.sidebar.date_input("Date", date.today())
if filtered_date:
    from_date = datetime.strptime(f"{filtered_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
    to_date = datetime.strptime(f"{filtered_date} 23:59:59", "%Y-%m-%d %H:%M:%S")
    orders_data = get_orders(from_date, to_date)
    
    prev_date = filtered_date - timedelta(days=1)
    from_date = datetime.strptime(f"{prev_date} 00:00:00", "%Y-%m-%d %H:%M:%S")
    to_date = datetime.strptime(f"{prev_date} 23:59:59", "%Y-%m-%d %H:%M:%S")
    prev_data = get_orders(from_date, to_date)


def percentage_change(current, previous):
    return ((current - previous) / previous * 100) if previous else np.nan


# KPIs
def kpi_metrics():
    # Previous Day
    prev_orders = prev_data["id"].nunique() if prev_data.shape[0] else 0
    prev_quantity = prev_data["quantity"].sum() if prev_data.shape[0] else 0
    prev_revenue = prev_data.groupby("id")["paid_amount"].first().sum() if prev_data.shape[0] else 0
    prev_delivery_charges = prev_data.groupby("id")["delivery_charges"].first().sum() if prev_data.shape[0] else 0
    prev_discount = prev_data.groupby("id")["discount"].first().sum() if prev_data.shape[0] else 0

    # Current Day
    total_orders = orders_data["id"].nunique()
    total_quantity = orders_data["quantity"].sum()
    total_revenue = orders_data.groupby("id")["paid_amount"].first().sum()
    total_delivery_charges = orders_data.groupby("id")["delivery_charges"].first().sum()
    total_discount = orders_data.groupby("id")["discount"].first().sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧾 Orders", total_orders, delta=f"{percentage_change(total_orders, prev_orders):.2f}%")
    col2.metric("📦 Quantity", total_quantity, delta=f"{percentage_change(total_quantity, prev_quantity):.2f}%")
    col3.metric("💰 Revenue", f"{total_revenue:,}", delta=f"{percentage_change(total_revenue, prev_revenue):.2f}%")
    col4.metric("🚚 Delivery Charges", f"{total_delivery_charges:,}")
    col5.metric("💸 Discount", f"{total_discount:,}")
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
        # Quantity - Donut Chart
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
        # By City
        agg_city_state_region = orders_data.groupby(["customer_city", "customer_state_region"]).agg({
            "quantity": "sum",
            "amount": "sum"
        }).reset_index()
        agg_city_state_region.columns = ["City", "State_Region", "Quantity", "Amount"]

        st.markdown("🏙️ By City")
        selected_metric_by_city = st.radio(
            label="Metric to display:",
            options=["Quantity", "Amount"],
            horizontal=True,
            key="metric_city"
        )

        bar_by_city = alt.Chart(agg_city_state_region) \
            .mark_bar() \
            .encode(
                x=alt.X("City", title="City"),
                y=alt.Y(selected_metric_by_city, title=selected_metric_by_city),
                tooltip=[
                    alt.Tooltip("City", title="City"),
                    alt.Tooltip(selected_metric_by_city, title=selected_metric_by_city, format=",.0f")
                ],
                color=alt.value("#4e79a7") if selected_metric_by_city == "Quantity" else alt.value("#f28e2b")
            )
        st.altair_chart(bar_by_city, use_container_width=True)

    with col3:
        # By Country
        agg_country = orders_data.groupby(["customer_country"]).agg({
            "quantity": "sum",
            "amount": "sum"
        }).reset_index()
        agg_country.columns = ["Country", "Quantity", "Amount"]

        st.markdown("🏙️ By Country")
        selected_metric_by_country = st.radio(
            label="Metric to display:",
            options=["Quantity", "Amount"],
            horizontal=True,
            key="metric_country"
        )

        bar_by_country = alt.Chart(agg_country) \
            .mark_bar() \
            .encode(
                x=alt.X("Country", title="Country"),
                y=alt.Y(selected_metric_by_country, title=selected_metric_by_country),
                tooltip=[
                    alt.Tooltip("Country", title="Country"),
                    alt.Tooltip(selected_metric_by_country, title=selected_metric_by_country, format=",.0f")
                ],
                color=alt.value("#4e79a7") if selected_metric_by_country == "Quantity" else alt.value("#f28e2b")
            )
        st.altair_chart(bar_by_country, use_container_width=True)

    st.divider()


# Order Summary
def order_summary():
    st.markdown("📋 Order Summary")

    summary_data = orders_data.copy()
    summary_data.drop_duplicates(subset=["order_no"], inplace=True)
    summary_data["customer"] = summary_data["customer_serial_no"] + " " + summary_data["customer_name"]
    summary_data = summary_data[["order_no", "customer", "ttl_quantity", "payment_type_name", "paid_amount"]]
    summary_data.columns = ["Order No", "Customer", "Quantity", "Payment Type", "Paid Amount"]

    summary_chart = alt.Chart(summary_data) \
        .mark_bar() \
        .encode(
            y=alt.Y("Order No", title="Order No", sort="-x"),
            x=alt.X("Paid Amount", title="Paid Amount"),
            color=alt.Color("Payment Type"),
            tooltip=[
                alt.Tooltip("Order No", title="Order No"),
                alt.Tooltip("Customer", title="Customer"),
                alt.Tooltip("Quantity", title="Quantity"),
                alt.Tooltip("Payment Type", title="Payment Type"),
                alt.Tooltip("Paid Amount", title="Paid Amount", format=",.0f")
            ]
        )
    st.altair_chart(summary_chart, use_container_width=True)


if orders_data.shape[0]:
    st.title("📊 Daily Dashboard")
    st.markdown(f"### Date: `{filtered_date}`")
    
    kpi_metrics()
    quantity_and_revenue_by_stock_category()
    revenue_breakdown()
    order_summary()
else:
    st.info("No data available 📭")
