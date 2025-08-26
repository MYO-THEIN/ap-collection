import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import calendar
import src.utils as utils
from src.report import get_orders, get_expenses

st.set_page_config(layout="wide")

if "orders_data" in st.session_state:
    del st.session_state["orders_data"]
if "expenses_data" in st.session_state:
    del st.session_state["expenses_data"]

# Filters
st.sidebar.header("🔎 Filters")
filtered_year = st.sidebar.number_input(    
    label="Year",
    min_value=2025,
    value=date.today().year
)

if filtered_year:
    from_date = datetime.strptime(f"{filtered_year}-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
    to_date = datetime.strptime(f"{filtered_year}-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")
    
    orders_data = get_orders(from_date, to_date)
    orders_data.drop_duplicates(subset=["order_no"], inplace=True)
    orders_data["date"] = pd.to_datetime(orders_data["date"])
    orders_data["month"] = orders_data["date"].dt.month
    orders_data = orders_data.groupby(["month", "payment_type_name"], as_index=False)["paid_amount"].sum()
    
    expenses_data = get_expenses(from_date, to_date)
    expenses_data["date"] = pd.to_datetime(expenses_data["date"])
    expenses_data["month"] = expenses_data["date"].dt.month
    expenses_data = expenses_data.groupby(["month", "expense_type_name"], as_index=False)["amount"].sum()


month_names = {
    1: "JAN", 2: "FEB", 3: "MAR", 4: "APR", 
    5: "MAY", 6: "JUN", 7: "JUL", 8: "AUG", 
    9: "SEP", 10: "OCT", 11: "NOV", 12: "DEC"
}

month_emojis = {
    1: "①", 2: "②", 3: "③", 4: "④",
    5: "⑤", 6: "⑥", 7: "⑦", 8: "⑧",
    9: "⑨", 10: "⑩", 11: "⑪", 12: "⑫"
}

annual_income = orders_data["paid_amount"].sum() if not orders_data.empty else 0
annual_expense = expenses_data["amount"].sum() if not expenses_data.empty else 0
annual_net = annual_income - annual_expense

def month_block(month):
    inc = orders_data[orders_data["month"] == month]
    exp = expenses_data[expenses_data["month"] == month]
    ttl_inc = inc["paid_amount"].sum()
    ttl_exp = exp["amount"].sum()
    net = ttl_inc - ttl_exp

    st.subheader(f"{month_emojis[month]} {month_names[month]}")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("💰 Income", f"{ttl_inc :,.0f}")
        if not inc.empty:
            for _, row in inc.iterrows():
                st.write(f"• {row['payment_type_name']}: **{row['paid_amount'] :,.0f}**")
        else:
            st.info("No data")

    with col2:
        st.metric("💸 Expense", f"{ttl_exp :,.0f}")
        if not exp.empty:
            for _, row in exp.iterrows():
                st.write(f"• {row['expense_type_name']}: **{row['amount'] :,.0f}**")
        else:
            st.info("No data")

    st.metric("💹 Net", f"{net :,.0f}", delta_color="inverse" if net < 0 else "normal")


st.title(f"💼 Income Statement {filtered_year}")
st.markdown("---")

# Annual KPI
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💰 Total Income", f"{annual_income / 1e5 :,.1f} L")
with col2:
    st.metric("💸 Total Expense", f"{annual_expense / 1e5 :,.1f} L")
with col3:
    st.metric("💹 Net", f"{annual_net / 1e5 :,.1f} L", delta_color="inverse" if annual_net < 0 else "normal")
st.markdown("---")

# Months
for i in range(0, 12, 2):
    col1, col2, col3 = st.columns([1, 0.3, 1])
    with col1:
        month_block(i + 1)
    if i + 2 <= 12:
        with col3:
            month_block(i + 2)
    
    st.divider()
