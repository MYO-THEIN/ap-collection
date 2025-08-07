import streamlit as st
import numpy as np
import plotly.express as px
from datetime import datetime, date, timedelta
from src.report import get_orders
import src.utils as utils

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


# KPIs
def kpi_metrics():
    # Previous Day
    prev_orders = prev_data["id"].nunique() if prev_data.shape[0] else 0
    prev_quantity = prev_data["quantity"].sum() if prev_data.shape[0] else 0
    prev_revenue = prev_data.groupby("id")["paid_amount"].first().sum() if prev_data.shape[0] else 0
    
    # Current Day
    total_orders = orders_data["id"].nunique()
    total_quantity = orders_data["quantity"].sum()
    total_revenue = orders_data.groupby("id")["paid_amount"].first().sum()
    total_delivery_charges = orders_data.groupby("id")["delivery_charges"].first().sum()
    total_discount = orders_data.groupby("id")["discount"].first().sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧾 Orders", total_orders, delta=f"{utils.percentage_change(total_orders, prev_orders):.2f}%")
    col2.metric("📦 Quantity", total_quantity, delta=f"{utils.percentage_change(total_quantity, prev_quantity):.2f}%")
    col3.metric("💰 Revenue", f"{total_revenue:,}", delta=f"{utils.percentage_change(total_revenue, prev_revenue):.2f}%")
    col4.metric("🚚 Delivery Charges", f"{total_delivery_charges:,}")
    col5.metric("💸 Discount", f"{total_discount:,}")
    st.divider()


# Quantity & Amount by Stock Category
def quantity_and_amount_by_stock_category():
    agg_stock_category = orders_data.groupby(["stock_category_id", "stock_category_name"]).agg({
        "quantity": "sum",
        "amount": "sum"
    }).reset_index()
    agg_stock_category.columns = ["Stock Category ID", "Stock Category", "Quantity", "Amount"]

    col1, col2 = st.columns(2)
    with col1:
        # Quantity - Donut Chart
        st.markdown("📦 Quantity by Stock Category")
        pie_quantity_by_stock_category = px.pie(
            data_frame=agg_stock_category, 
            names="Stock Category", 
            values="Quantity",
            hole=0.4
        ) \
        .update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Quantity: %{value}"
            )
        )
        st.plotly_chart(pie_quantity_by_stock_category, use_container_width=True)
    
    with col2:
        # Amount - Bar Chart
        st.markdown("💰 Amount by Stock Category")
        bar_amount_by_stock_category = px.bar(
            data_frame=agg_stock_category.sort_values(by="Amount", ascending=False), 
            x="Stock Category",
            y="Amount",
            color="Stock Category"
        ) \
        .update_layout(yaxis_tickformat=",.0f") \
        .update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Amount: %{value}"
            )
        )
        st.plotly_chart(bar_amount_by_stock_category, use_container_width=True)

    st.divider()


# Revenue Breakdown
def revenue_breakdown():
    col1, col2 = st.columns(2)
    with col1:
        # By Payment Type - Pie Chart
        agg_payment_type = orders_data.drop_duplicates(subset=["id"]).groupby(["payment_type_id", "payment_type_name"]).agg({
            "paid_amount": "sum"
        }).reset_index()
        agg_payment_type.columns = ["Payment Type ID", "Payment Type", "Paid Amount"]

        st.markdown("💳 Revenue by Payment Type")
        pie_revenue_by_payment_type = px.pie(
            data_frame=agg_payment_type, 
            names="Payment Type", 
            values="Paid Amount",
            hole=0.4
        ) \
        .update_traces(
            hovertemplate=(
                "<b>%{label}</b><br>"
                "Revenue: %{value}"
            )
        )
        st.plotly_chart(pie_revenue_by_payment_type, use_container_width=True)

    with col2:
        # By City / Country - Bar Chart
        option_city_country = st.radio(
            label="🏙️ Display By",
            options=["City", "Country"],
            horizontal=True,
            key="metric_city"
        )
        if option_city_country == "City":
            agg_city_country = orders_data.groupby(["customer_city", "customer_state_region"]).agg({
                "quantity": "sum",
                "amount": "sum"
            }).reset_index()
            agg_city_country.columns = ["City", "State_Region", "Quantity", "Amount"]
        elif option_city_country == "Country":
            agg_city_country = orders_data.groupby(["customer_country"]).agg({
                "quantity": "sum",
                "amount": "sum"
            }).reset_index()
            agg_city_country.columns = ["Country", "Quantity", "Amount"]

        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            # Quantity
            bar_quantity = px.bar(
                data_frame=agg_city_country.sort_values(by="Quantity", ascending=False), 
                x="City" if option_city_country == "City" else "Country",
                y="Quantity",
                color="City" if option_city_country == "City" else "Country"
            ) \
            .update_traces(
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Quantity: %{value}"
                )
            )
            st.plotly_chart(bar_quantity, use_container_width=True)

        with sub_col2:
            # Amount
            bar_amount = px.bar(
                data_frame=agg_city_country.sort_values(by="Amount", ascending=False), 
                x="City" if option_city_country == "City" else "Country",
                y="Amount",
                color="City" if option_city_country == "City" else "Country"
            ) \
            .update_layout(yaxis_tickformat=",.0f") \
            .update_traces(
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Amount: %{value}"
                )
            )
            st.plotly_chart(bar_amount, use_container_width=True)

    st.divider()


# Daily Summary
def daily_summary():
    summary_data = orders_data.copy()
    summary_data.drop_duplicates(subset=["order_no"], inplace=True)
    summary_data["customer"] = summary_data["customer_serial_no"] + " " + summary_data["customer_name"]
    summary_data = summary_data[["order_no", "customer", "ttl_quantity", "payment_type_name", "paid_amount"]]
    summary_data.columns = ["Order No", "Customer", "Quantity", "Payment Type", "Paid Amount"]

    st.markdown("📋 Daily Summary")
    bar_summary = px.bar(
        data_frame=summary_data.sort_values(by="Paid Amount", ascending=True), 
        x="Paid Amount",
        y="Order No",
        color="Payment Type",
        custom_data=["Order No", "Customer", "Quantity", "Payment Type", "Paid Amount"]
    ) \
    .update_layout(xaxis_tickformat=",.0f") \
    .update_traces(
        hovertemplate=(
            "Order No: %{customdata[0]}<br>"
            "Customer: %{customdata[1]}<br>"
            "Quantity: %{customdata[2]}<br>"
            "Payment Type: %{customdata[3]}<br>"
            "Paid Amount: %{customdata[4]:,}"
        )
    )
    st.plotly_chart(bar_summary, use_container_width=True)


if orders_data.shape[0]:
    st.title("📊 Daily Dashboard")
    st.markdown(f"### Date: `{filtered_date}`")
    
    kpi_metrics()
    quantity_and_amount_by_stock_category()
    revenue_breakdown()
    daily_summary()
else:
    st.info("No data available 📭")
