import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="Yearly Income Statement")

# ---- Sample aggregated data
months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
income_types = ["Sales", "Service Fees", "Interest"]
expense_types = ["Rent", "Salaries", "Utilities"]

np.random.seed(42)
income_df = pd.DataFrame({
    "month_name": np.random.choice(months, 50),
    "payment_type": np.random.choice(income_types, 50),
    "amount": np.random.randint(500, 5000, 50)
})
expense_df = pd.DataFrame({
    "month_name": np.random.choice(months, 50),
    "expense_type": np.random.choice(expense_types, 50),
    "amount": np.random.randint(300, 4000, 50)
})

# Aggregate
income_summary = income_df.groupby(["month_name", "payment_type"])["amount"].sum().reset_index()
expense_summary = expense_df.groupby(["month_name", "expense_type"])["amount"].sum().reset_index()

total_income_per_month = income_summary.groupby("month_name")["amount"].sum()
total_expense_per_month = expense_summary.groupby("month_name")["amount"].sum()

month_order = pd.CategoricalDtype(months, ordered=True)
income_summary["month_name"] = income_summary["month_name"].astype(month_order)
expense_summary["month_name"] = expense_summary["month_name"].astype(month_order)
income_summary = income_summary.sort_values("month_name")
expense_summary = expense_summary.sort_values("month_name")

st.markdown("<h2 style='text-align:center;'>Yearly Income Statement</h2>", unsafe_allow_html=True)
st.markdown("---")

# ---- CSS for card style
st.markdown("""
<style>
.month-card {
    border: 1px solid #ddd;
    border-radius: 10px;
    padding: 15px;
    margin: 5px 0;
    background-color: #fafafa;
    box-shadow: 0px 2px 5px rgba(0,0,0,0.1);
}
.month-title {
    font-size: 20px; 
    font-weight: bold; 
    margin-bottom: 10px;
    text-align: center;
}
.net-positive {
    color: green; 
    font-weight: bold;
}
.net-negative {
    color: red; 
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# Helper to render card
def render_month_card(month):
    inc = income_summary[income_summary["month_name"] == month]
    exp = expense_summary[expense_summary["month_name"] == month]
    net = total_income_per_month.get(month, 0) - total_expense_per_month.get(month, 0)
    net_class = "net-positive" if net >= 0 else "net-negative"

    card_html = f"<div class='month-card'><div class='month-title'>{month}</div>"

    if not inc.empty:
        card_html += "<b>Income:</b><ul>"
        for _, row in inc.iterrows():
            card_html += f"<li>{row['payment_type']}: ${row['amount']:,.0f}</li>"
        card_html += "</ul>"
    else:
        card_html += "<b>Income:</b> No data<br>"

    if not exp.empty:
        card_html += "<b>Expense:</b><ul>"
        for _, row in exp.iterrows():
            card_html += f"<li>{row['expense_type']}: ${row['amount']:,.0f}</li>"
        card_html += "</ul>"
    else:
        card_html += "<b>Expense:</b> No data<br>"

    card_html += f"<b>Net:</b> <span class='{net_class}'>${net:,.0f}</span></div>"
    st.markdown(card_html, unsafe_allow_html=True)

# Render 2 columns per row
unique_months = income_summary["month_name"].dropna().unique().tolist()
for i in range(0, len(unique_months), 2):
    cols = st.columns(2)
    with cols[0]:
        render_month_card(unique_months[i])
    if i + 1 < len(unique_months):
        with cols[1]:
            render_month_card(unique_months[i+1])
