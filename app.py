import streamlit as st
import src.utils as utils

st.set_page_config(page_title="AP Collection", page_icon="🌴")

# About Us
about_us_pg = st.Page(
    title="About Us",
    icon="🌟",
    page="pages/1_About_Us.py"
)

# Payment Type
payment_type_pg = st.Page(
    title="Payment Type",
    icon="💰",
    page="pages/2_Payment_Type.py"
)

# Stock Category
stock_category_pg = st.Page(
    title="Stock Category",
    icon="👕",
    page="pages/3_Stock_Category.py"
)

# Customer
customer_pg = st.Page(
    title="Customer",
    icon="🧑",
    page="pages/4_Customer.py"
)

# Order
order_pg = st.Page(
    title="Order",
    icon="🛒",
    page="pages/5_Order.py"
)

# Daily Dashboard
daily_report_pg = st.Page(
    title="Daily Dashboard",
    icon="📊",
    page="pages/6_Daily_Dashboard.py"
)

# Monthly Report
monthly_report_pg = st.Page(
    title="Monthly Report",
    icon="🗓️",
    page="pages/7_Monthly_Report.py"
)

pg = st.navigation({
    "Process": [
        about_us_pg, 
        payment_type_pg, 
        stock_category_pg, 
        customer_pg, 
        order_pg
    ],
    "Reports": [
        daily_report_pg, 
        monthly_report_pg
    ]
})
pg.run()

# PostgreSQL connection
st.session_state["postgresql"] = utils.get_postgresql_connection()
