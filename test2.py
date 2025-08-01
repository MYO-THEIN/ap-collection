import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date, timedelta

st.set_page_config("📈 Sales Dashboard", layout="wide")

# --- Simulated Data (Replace with your actual DB/query) ---
np.random.seed(1)

# Mappings
payment_types = {1: "Cash", 2: "Card", 3: "Credit"}
stock_categories = {1: "Food", 2: "Drinks", 3: "Supplies", 4: "Misc"}
cities = ["Yangon", "Mandalay", "Naypyidaw"]
countries = ["Myanmar", "Thailand", "Singapore"]

# Sample sales
N = 100
sales = pd.DataFrame({
    "date": [date.today() - timedelta(days=np.random.randint(0, 5)) for _ in range(N)],
    "order_no": [f"ORD-{1000+i}" for i in range(N)],
    "customer_id": np.random.randint(1, 50, N),
    "ttl_quantity": np.random.randint(1, 10, N),
    "ttl_amount": np.random.uniform(1000, 5000, N),
    "delivery_charges": np.random.uniform(500, 1000, N),
    "payment_type_id": np.random.choice([1, 2, 3], N),
    "city": np.random.choice(cities, N),
    "country": np.random.choice(countries, N),
}).assign(
    paid_amount=lambda df: df.ttl_amount + df.delivery_charges
)

# Sample sale details
sale_details = pd.DataFrame({
    "order_no": np.random.choice(sales["order_no"], 300),
    "stock_category_id": np.random.choice([1, 2, 3, 4], 300),
    "quantity": np.random.randint(1, 5, 300),
    "amount": np.random.uniform(100, 2000, 300)
})

# Filters
st.sidebar.header("🔎 Filter")
selected_date = st.sidebar.date_input("Select Date", date.today())
filtered_sales = sales[sales["date"] == selected_date]
filtered_details = sale_details.merge(filtered_sales[["order_no"]], on="order_no")

# KPIs
st.title("📊 Daily Sales Dashboard")
st.markdown(f"### Date: `{selected_date}`")

col1, col2, col3, col4 = st.columns(4)
col1.metric("🧾 Total Orders", len(filtered_sales))
col2.metric("📦 Total Quantity", int(filtered_sales["ttl_quantity"].sum()))
col3.metric("💰 Total Revenue", f"{filtered_sales['paid_amount'].sum():,.0f} MMK")
col4.metric("🚚 Delivery Charges", f"{filtered_sales['delivery_charges'].sum():,.0f} MMK")

st.divider()

# --- Middle Charts: Quantity & Revenue by Stock Category ---
cat_summary = filtered_details.groupby("stock_category_id").agg({
    "quantity": "sum",
    "amount": "sum"
}).reset_index()
cat_summary["Category"] = cat_summary["stock_category_id"].map(stock_categories)

mid1, mid2 = st.columns(2)

# Pie/Donut Chart - Quantity
with mid1:
    st.subheader("📦 Quantity by Stock Category")
    pie = alt.Chart(cat_summary).mark_arc(innerRadius=40).encode(
        theta="quantity",
        color="Category",
        tooltip=["Category", "quantity"]
    )
    st.altair_chart(pie, use_container_width=True)

# Bar Chart - Revenue
with mid2:
    st.subheader("💰 Revenue by Stock Category")
    bar = alt.Chart(cat_summary).mark_bar().encode(
        x=alt.X("amount", title="Revenue"),
        y=alt.Y("Category", sort='-x'),
        tooltip=["Category", "amount"]
    )
    st.altair_chart(bar, use_container_width=True)

st.divider()

# --- Lower Row (3 Columns) ---
l1, l2, l3 = st.columns(3)

# 1. Revenue by Payment Type
with l1:
    st.subheader("💳 Revenue by Payment Type")
    payment_summary = filtered_sales.groupby("payment_type_id")["paid_amount"].sum().reset_index()
    payment_summary["Payment"] = payment_summary["payment_type_id"].map(payment_types)
    pie_payment = alt.Chart(payment_summary).mark_arc(innerRadius=40).encode(
        theta="paid_amount",
        color="Payment",
        tooltip=["Payment", "paid_amount"]
    )
    st.altair_chart(pie_payment, use_container_width=True)

print("filtered_sales.columns: ", filtered_sales.columns)

# 2. Revenue & Quantity by City
with l2:
    st.subheader("🏙️ By City")
    city_summary = filtered_sales.groupby("city").agg(
        Revenue=("paid_amount", "sum"),
        Quantity=("ttl_quantity", "sum")
    ).reset_index()
    city_chart = alt.Chart(city_summary).transform_fold(
        ["Revenue", "Quantity"], as_=["Metric", "Value"]
    ).mark_bar().encode(
        x=alt.X("city:N", title="City"),
        y=alt.Y("Value:Q"),
        color="Metric:N",
        column="Metric:N",
        # tooltip=["city", "Metric", "Value"]
        tooltip=[
            alt.Tooltip("city:N"),
            alt.Tooltip("Metric:N"),
            alt.Tooltip("Value:Q")
        ]
    )
    st.altair_chart(city_chart, use_container_width=True)

# 3. Revenue & Quantity by Country
with l3:
    st.subheader("🌍 By Country")
    country_summary = filtered_sales.groupby("country").agg(
        Revenue=("paid_amount", "sum"),
        Quantity=("ttl_quantity", "sum")
    ).reset_index()
    country_chart = alt.Chart(country_summary).transform_fold(
        ["Revenue", "Quantity"], as_=["Metric", "Value"]
    ).mark_bar().encode(
        x=alt.X("country:N", title="Country"),
        y=alt.Y("Value:Q"),
        color="Metric:N",
        column="Metric:N",
        # tooltip=["country", "Metric", "Value"]
        tooltip=[
            alt.Tooltip("country:N"),
            alt.Tooltip("Metric:N"),
            alt.Tooltip("Value:Q")
        ]
    )
    st.altair_chart(country_chart, use_container_width=True)

st.divider()

# --- Order Summary Chart ---
st.subheader("📋 Order Summary")

if not filtered_sales.empty:
    latest_orders = (
        filtered_sales[["order_no", "ttl_quantity", "paid_amount", "payment_type_id"]]
        .assign(Payment=lambda df: df["payment_type_id"].map(payment_types))
    )

    order_chart = alt.Chart(latest_orders).mark_bar().encode(
        y=alt.Y("order_no:N", title="Order No", sort="-x"),
        x=alt.X("paid_amount:Q", title="Paid Amount"),
        color=alt.Color("Payment:N"),
        tooltip=["order_no", "ttl_quantity", "paid_amount", "Payment"]
    ).properties(height=400)
    
    st.altair_chart(order_chart, use_container_width=True)
else:
    st.info("No order data for selected date.")
