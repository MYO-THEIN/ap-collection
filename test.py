import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from datetime import date, timedelta

st.set_page_config(page_title="Daily Sales Dashboard", layout="wide")

# --- Simulate Sample Data ---
np.random.seed(42)

# Constants
payment_types = {1: "Cash", 2: "Card", 3: "Credit"}
stock_categories = {1: "Food", 2: "Drinks", 3: "Supplies", 4: "Misc"}

# Generate sample sales
num_sales = 100
sales = pd.DataFrame({
    "date": [date.today() - timedelta(days=np.random.randint(0, 10)) for _ in range(num_sales)],
    "order_no": [f"ORD-{1000+i}" for i in range(num_sales)],
    "customer_id": np.random.randint(1, 10, size=num_sales),
    "ttl_quantity": np.random.randint(1, 10, size=num_sales),
    "ttl_amount": np.random.uniform(1000, 10000, size=num_sales).round(2),
    "delivery_charges": np.random.uniform(0, 1000, size=num_sales).round(2),
    "payment_type_id": np.random.choice(list(payment_types.keys()), size=num_sales),
    "paid_amount": lambda df: df["ttl_amount"] + df["delivery_charges"]
}).assign(
    paid_amount=lambda df: df["ttl_amount"] + df["delivery_charges"]
)

# Generate sample sale details
sale_details = pd.DataFrame({
    "order_no": np.random.choice(sales["order_no"], size=300),
    "stock_category_id": np.random.choice(list(stock_categories.keys()), size=300),
    "quantity": np.random.randint(1, 5, size=300),
    "amount": np.random.uniform(100, 2000, size=300).round(2),
})

# --- Sidebar Filters ---
st.sidebar.header("🔎 Filter")
selected_date = st.sidebar.date_input("Select date", date.today())
selected_payment = st.sidebar.multiselect("Payment Types", options=payment_types.values(), default=list(payment_types.values()))

# --- Filter Data ---
filtered_sales = sales[sales["date"] == selected_date]
filtered_sales = filtered_sales[filtered_sales["payment_type_id"].map(payment_types) \
                                .isin(selected_payment)]

# --- KPIs ---
st.title("📊 Daily Sales Dashboard")
st.markdown(f"### Date: `{selected_date}`")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Total Orders", len(filtered_sales))
kpi2.metric("Total Quantity", int(filtered_sales["ttl_quantity"].sum()))
kpi3.metric("Total Revenue", f"{filtered_sales['paid_amount'].sum():,.2f} MMK")
kpi4.metric("Delivery Charges", f"{filtered_sales['delivery_charges'].sum():,.2f} MMK")

st.divider()

# --- Payment Type Breakdown ---
st.subheader("💰 Revenue by Payment Type")
if not filtered_sales.empty:
    payment_summary = (
        filtered_sales
        .groupby("payment_type_id")["paid_amount"]
        .sum()
        .reset_index()
    )
    payment_summary["payment_type"] = payment_summary["payment_type_id"].map(payment_types)

    chart = alt.Chart(payment_summary).mark_bar().encode(
        x=alt.X("payment_type", title="Payment Type"),
        y=alt.Y("paid_amount", title="Paid Amount"),
        tooltip=["payment_type", "paid_amount"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("No data for selected date/payment type.")

# --- Top Selling Categories ---
st.subheader("📦 Top Categories Sold")
joined = sale_details.merge(sales[["order_no", "date"]], on="order_no")
joined = joined[joined["date"] == selected_date]

if not joined.empty:
    cat_summary = (
        joined
        .groupby("stock_category_id")[["quantity", "amount"]]
        .sum()
        .reset_index()
    )
    cat_summary["Category"] = cat_summary["stock_category_id"].map(stock_categories)

    st.dataframe(
        cat_summary[["Category", "quantity", "amount"]]
        .rename(columns={"quantity": "Total Quantity", "amount": "Total Amount"})
        .sort_values("Total Amount", ascending=False),
        use_container_width=True
    )
else:
    st.info("No sale details for selected date.")

# --- Detailed Sale Table ---
st.subheader("🧾 Sale Transactions")

if not filtered_sales.empty:
    st.dataframe(
        filtered_sales[[
            "order_no", "customer_id", "ttl_quantity", "ttl_amount",
            "delivery_charges", "paid_amount", "payment_type_id"
        ]].rename(columns={
            "order_no": "Order No",
            "customer_id": "Customer",
            "ttl_quantity": "Quantity",
            "ttl_amount": "Subtotal",
            "delivery_charges": "Delivery",
            "paid_amount": "Paid",
            "payment_type_id": "Payment Type"
        }).assign(**{
            "Payment Type": lambda df: df["Payment Type"].map(payment_types)
        }),
        use_container_width=True,
        height=300
    )
else:
    st.info("No sales found for selected filters.")
