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

def render_month_card(mth):
    inc = orders_data[orders_data["month"] == mth]
    exp = expenses_data[expenses_data["month"] == mth]
    ttl_inc = inc["paid_amount"].sum()
    ttl_exp = exp["amount"].sum()
    net = ttl_inc - ttl_exp
    net_class = "net-positive" if net >= 0 else "net-negative"

    card_html = f"<div class='month-card'><div class='month-title'>{month_names[mth]}</div>"

    # Incomes
    if not inc.empty:
        card_html += f"<b>Income</b> <h3>{ttl_inc:,.0f}</h3><ul>"
        for _, row in inc.iterrows():
            card_html += f"<li>{row['payment_type_name']}: {row['paid_amount']:,.0f}</li>"
        card_html += "</ul>"
    else:
        card_html += "<b>Income</b><br>No data<br>"

    # Expenses
    if not exp.empty:
        card_html += f"<b>Expense</b> <h3>{ttl_exp:,.0f}</h3><ul>"
        for _, row in exp.iterrows():
            card_html += f"<li>{row['expense_type_name']}: {row['amount']:,.0f}</li>"
        card_html += "</ul>"
    else:
        card_html += "<b>Expense</b><br>No data<br>"

    card_html += f"<b>Net</b> <h3 class='{net_class}'>{net:,.0f}</h3></div>"
    st.markdown(card_html, unsafe_allow_html=True)


st.markdown(f"<h3 style='text-align: center;'>Income Statement for Year {filtered_year}</h3>", unsafe_allow_html=True)
st.markdown("---")

# ---- CSS for card style
st.markdown(
    """
    <style>
    .month-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
        background-color: #fafafa;
        box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
    }
    .month-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        text-align: center;
    }
    .net-positive {
        color: green;
    }
    .net-negative {
        color: red;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

for i in range(0, 12, 2):
    cols = st.columns(2)
    with cols[0]:
        render_month_card(i + 1)
    if i + 1 < 12:
        with cols[1]:
            render_month_card(i + 2)
