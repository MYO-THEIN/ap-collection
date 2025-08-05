import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import plotly.express as px 
from datetime import datetime, date
import calendar
from src.report import get_orders

st.set_page_config(layout="wide")

if "orders_data" in st.session_state:
    del st.session_state["orders_data"]

# Filters
st.sidebar.header("🔎 Filters")
filtered_year = st.sidebar.number_input(
    label="Year",
    min_value=2025,
    value=date.today().year
)
filtered_month = st.sidebar.selectbox(
    label="Month",
    options=[f"{i:02d}" for i in range(1, 13)],
    format_func=lambda x: calendar.month_name[int(x)],
    index=date.today().month - 1
)
if filtered_year and filtered_month:
    last_day_of_month = calendar.monthrange(int(filtered_year), int(filtered_month))[1]

    from_date = datetime.strptime(f"{filtered_year}-{filtered_month}-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    to_date = datetime.strptime(f"{filtered_year}-{filtered_month}-{last_day_of_month} 23:59:59", "%Y-%m-%d %H:%M:%S")
    orders_data = get_orders(from_date, to_date)


# KPIs
def kpi_metrics():
    total_orders = orders_data["id"].nunique()
    total_quantity = orders_data["quantity"].sum()
    total_revenue = orders_data.groupby("id")["paid_amount"].first().sum()
    total_delivery_charges = orders_data.groupby("id")["delivery_charges"].first().sum()
    total_discount = orders_data.groupby("id")["discount"].first().sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🧾 Orders", total_orders)
    col2.metric("📦 Quantity", total_quantity)
    col3.metric("💰 Revenue", f"{total_revenue / 1e5:.1f} L")
    col4.metric("🚚 Delivery Charges", f"{total_delivery_charges:,}")
    col5.metric("💸 Discount", f"{total_discount:,}")

    st.divider()


# Daily Quantity & Revenue
def daily_quantity_and_revenue():
    col1, col2 = st.columns(2)
    with col1:  
        # Quantity - Bar Chart
        agg_daily_quantity = orders_data.groupby(["date"]).agg({
            "quantity": "sum"
        }).reset_index()
        agg_daily_quantity.columns = ["Date", "Quantity"]

        st.markdown("📦 Daily Quantity")
        bar_daily_quantity = alt.Chart(agg_daily_quantity) \
            .mark_bar(color="#4daf4a") \
            .encode(
                x=alt.X("Date", title="Date", axis=alt.Axis(format="%Y-%m-%d")),
                y=alt.Y("Quantity", title="Quantity"),
                tooltip=[
                    alt.Tooltip("Date", title="Date"),
                    alt.Tooltip("Quantity", title="Quantity")
                ]
            )
        st.altair_chart(bar_daily_quantity, use_container_width=True)
    
    with col2:
        # Revenue - Bar Chart
        agg_daily_revenue = orders_data.drop_duplicates(subset=["order_no"]).groupby(["date"]).agg({
            "paid_amount": "sum"
        }).reset_index()
        agg_daily_revenue.columns = ["Date", "Revenue"]

        st.markdown("💰 Daily Revenue")
        bar_daily_revenue = alt.Chart(agg_daily_revenue) \
            .mark_bar(color="#d62728") \
            .encode(
                x=alt.X("Date", title="Date", axis=alt.Axis(format="%Y-%m-%d")),
                y=alt.Y("Revenue", title="Revenue"),
                tooltip=[
                    alt.Tooltip("Date", title="Date"),
                    alt.Tooltip("Revenue", title="Revenue", format=",.0f")
                ]
            )
        st.altair_chart(bar_daily_revenue, use_container_width=True)

    st.divider()


# Stock Category Insights
def quantity_and_amount_by_stock_category():
    agg_stock_category = orders_data.groupby(["stock_category_name"]).agg({
        "quantity": "sum",
        "amount": "sum"
    }).reset_index()
    agg_stock_category.columns = ["Stock Category", "Quantity", "Amount"]

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
            hovertemplate="<b>%{label}</b><br>Quantity: %{value}"
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
            hovertemplate="<b>%{label}</b><br>Amount: %{value}"
        )
        st.plotly_chart(bar_amount_by_stock_category, use_container_width=True)

    st.divider()


# Payment Type Insights
def payment_type_insights():
    agg_payment_type = orders_data.groupby(["date", "payment_type_name"]).agg({
        "paid_amount": "sum"
    }).reset_index()

    # percent contribution
    agg_payment_type["total"] = agg_payment_type.groupby("date")["paid_amount"].transform("sum")
    agg_payment_type["percent"] = agg_payment_type["paid_amount"] / agg_payment_type["total"] * 100

    agg_payment_type.columns = ["Date", "Payment Type", "Revenue", "Total", "Percent"]


    st.markdown("💳 Revenue by Payment Type")
    # line_payment_type = alt.Chart(agg_payment_type) \
    #     .mark_line(point=True, interpolate="monotone") \
    #     .encode(
    #         x=alt.X("Date", title="Date", axis=alt.Axis(format="%Y-%m-%d")),
    #         y=alt.Y("Revenue", title="Revenue"),
    #         color="Payment Type",
    #         tooltip=[
    #             alt.Tooltip("Date", title="Date"),
    #             alt.Tooltip("Payment Type", title="Payment Type"),
    #             alt.Tooltip("Revenue", title="Revenue", format=",.0f")
    #         ]
    #     )
    # st.altair_chart(line_payment_type, use_container_width=True)

    # Heatmap
    heat_data = agg_payment_type.pivot(index="Date", columns="Payment Type", values="Revenue").fillna(0)
    fig_heatmap = px.imshow(
        heat_data.T,
        aspect="auto",
        labels=dict(x="Date", y="Payment Type", color="Revenue")
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        # Sunburst Chart
        fig_sb = px.sunburst(
            data_frame=agg_payment_type,
            path=["Payment Type", "Date"],
            values="Revenue"
        )
        st.plotly_chart(fig_sb, use_container_width=True)

    with col2:
        # Treemap
        agg = agg_payment_type.groupby("Payment Type")["Revenue"].sum().reset_index()
        fig_treemap = px.treemap(
            agg,
            path=["Payment Type"],
            values="Revenue"
        )
        st.plotly_chart(fig_treemap, use_container_width=True)

    # Stacked Bar Chart
    stack_order = (
        agg_payment_type.groupby("Payment Type")["Percent"].mean().sort_values(ascending=False).index.tolist()
    )

    fig_stacked_bar = px.bar(
        data_frame=agg_payment_type,
        x="Date",
        y="Percent",
        color="Payment Type",
        custom_data=["Date", "Payment Type", "Revenue", "Percent"],
        category_orders={"Payment Type": stack_order}
    ) \
    .update_layout(
        barmode="stack"
    ) \
    .update_traces(
        hovertemplate="Date: %{customdata[0]}<br>Payment Type: %{customdata[1]}<br>Revenue: %{customdata[2]:,}<br>Percent: %{customdata[3]:.2f}%",
    )
    st.plotly_chart(fig_stacked_bar, use_container_width=True)

    st.divider()


if orders_data.shape[0]:
    st.title("🗓️ Monthly Report")
    st.markdown(f"### Month: `{filtered_year}-{filtered_month}`")

    kpi_metrics()
    daily_quantity_and_revenue()
    quantity_and_amount_by_stock_category()
    payment_type_insights()
else:
    st.info("No data available 📭")
