import streamlit as st
import bcrypt
import src.utils as utils
from src.user import get_users

st.set_page_config(page_title="AP Collections", page_icon="🌴")

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "role_name" not in st.session_state:
    st.session_state["role_name"] = None

def check_credentials(users, username, password):
    result = {
        "valid": False,
        "user_name": None,
        "role_name": None,
        "permissions": None
    }

    for _, row in users.iterrows():
        if row["user_name"] == username and bcrypt.checkpw(password.encode("utf-8"), row["password"].encode("utf-8")):
            result["valid"] = True
            result["user_name"] = row["user_name"]
            result["role_name"] = row["role_name"]
            result["permissions"] = row["permissions"]
            break

    return result

def hide_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="stHeader"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True
    )


def show_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: block;}
        [data-testid="stHeader"] {display: block;}
        </style>
        """,
        unsafe_allow_html=True
    )


# PostgreSQL connection
st.session_state["postgresql"] = utils.get_postgresql_connection()


# About Us
about_us_pg = st.Page(
    title="About Us", icon="🌟", page="pages/1_About_Us.py",
    default=st.session_state["role_name"] not in ["Staff", "Viewer"]
)

# Payment Type
payment_type_pg = st.Page(title="Payment Type", icon="💰", page="pages/2_Payment_Type.py")

# Stock Category
stock_category_pg = st.Page(title="Stock Category", icon="👕", page="pages/3_Stock_Category.py")

# Customer
customer_pg = st.Page(title="Customer", icon="🧑", page="pages/4_Customer.py")

# Order
order_pg = st.Page(title="Order", icon="🛒", page="pages/5_Order.py")

# Delivery
delivery_pg = st.Page(
    title="Delivery", icon="🚚", page="pages/8_Delivery.py",
    default=st.session_state["role_name"] == "Staff"
)

# Expense Type
expense_type_pg = st.Page(title="Expense Type", icon="🧾", page="pages/9_Expense_Type.py")

# Expense
expense_pg = st.Page(title="Expense", icon="💸", page="pages/10_Expense.py")

# Daily Dashboard
daily_dashboard_pg = st.Page(
    title="Daily Dashboard", icon="📊", page="pages/6_Daily_Dashboard.py",
    default=st.session_state["role_name"] == "Viewer"
)

# Monthly Report
monthly_report_pg = st.Page(title="Monthly Report", icon="🗓️", page="pages/7_Monthly_Report.py")

# Income Statement
income_statement_pg = st.Page(title="Income Statement", icon="💼", page="pages/11_Income_Statement.py")

# Process Group
pages_process = {
    "About Us": about_us_pg,
    "Payment Type": payment_type_pg,
    "Stock Category": stock_category_pg,
    "Customer": customer_pg,
    "Order": order_pg,
    "Delivery": delivery_pg,
    "Expense Type": expense_type_pg,
    "Expense": expense_pg
}

# Report Group
pages_report = {
    "Daily Dashboard": daily_dashboard_pg,
    "Monthly Report": monthly_report_pg,
    "Income Statement": income_statement_pg
}

users = get_users()

if st.session_state["authenticated"] == False:
    # Login Form
    hide_sidebar()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # centered
        st.markdown(
            """
            <style>
            .block-container {
                max-width: 650px;
                margin: auto;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #e0f7fa, #fce4ec);
                padding: 20px;
                border-radius: 20px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                text-align: center;
            ">
                <h3 style="
                    font-family: 'Trebuchet MS', sans-serif;
                    font-size: 21px;
                    color: #333;
                    margin: 0;
                ">🌴 AP Collections</h3>
                <p style="color: #666; font-size: 14px; margin-top: 8px;">
                    Find Your Inner Diva with AP Collections
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form(key="login_form", width="stretch", height="stretch"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🚀 Login")

            if submitted:
                result = check_credentials(users, username, password)
                if result["valid"]:
                    # save in session state
                    st.session_state["authenticated"] = True
                    st.session_state["user_name"] = result["user_name"]
                    st.session_state["role_name"] = result["role_name"]
                    st.session_state["permissions"] = result["permissions"]
                    st.success("Login successful 🎉")
                    st.rerun()
                else:
                    st.error("Invalid username/password ❌")
else:
    st.sidebar.success(f"Welcome, {st.session_state["user_name"]} 👋")
    logout = st.sidebar.button("🚪 Logout")
    if logout:
        # clear the session state
        st.session_state.clear()
        st.rerun()

    process_list = [p_obj for p_name, p_obj in pages_process.items() if p_name in st.session_state["permissions"].keys()]
    report_list = [p_obj for p_name, p_obj in pages_report.items() if p_name in st.session_state["permissions"].keys()]

    if process_list or report_list:
        pg = st.navigation({
            "Process": process_list,
            "Report": report_list
        }, position="top")

        pg.run()
