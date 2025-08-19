import streamlit as st
import src.utils as utils
from src.user import get_users
import bcrypt

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
        </style>
        """,
        unsafe_allow_html=True
    )


def show_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {display: block;}
        </style>
        """,
        unsafe_allow_html=True
    )


def reset_session():
    st.session_state.clear()


st.set_page_config(page_title="AP Collection", page_icon="🌴", layout="centered")

# PostgreSQL connection
st.session_state["postgresql"] = utils.get_postgresql_connection()

# pages
about_us_pg = st.Page(
    title="About Us", icon="🌟", page="pages/1_About_Us.py",
    default=st.session_state["role_name"] not in ["Staff", "Viewer"]
)
payment_type_pg = st.Page(title="Payment Type", icon="💰", page="pages/2_Payment_Type.py")
stock_category_pg = st.Page(title="Stock Category", icon="👕", page="pages/3_Stock_Category.py")
customer_pg = st.Page(title="Customer", icon="🧑", page="pages/4_Customer.py")
order_pg = st.Page(title="Order", icon="🛒", page="pages/5_Order.py")
delivery_pg = st.Page(
    title="Delivery", icon="🚚", page="pages/8_Delivery.py",
    default=st.session_state["role_name"] == "Staff"
)
daily_dashboard_pg = st.Page(
    title="Daily Dashboard", icon="📊", page="pages/6_Daily_Dashboard.py",
    default=st.session_state["role_name"] == "Viewer"
)
monthly_report_pg = st.Page(title="Monthly Report", icon="🗓️", page="pages/7_Monthly_Report.py")

pages_process = {
    "About Us": about_us_pg,
    "Payment Type": payment_type_pg,
    "Stock Category": stock_category_pg,
    "Customer": customer_pg,
    "Order": order_pg,
    "Delivery": delivery_pg
}

pages_report = {
    "Daily Dashboard": daily_dashboard_pg,
    "Monthly Report": monthly_report_pg
}

users = get_users()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if st.session_state["authenticated"] == False:
    # Login Form
    hide_sidebar()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="
                background: linear-gradient(135deg, #e0f7fa, #fce4ec);
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
                text-align: center;
            ">
                <h3 style="
                    font-family: 'Trebuchet MS', sans-serif;
                    font-size: 26px;
                    color: #333;
                    margin: 0;
                ">🌴 AP Collection</h3>
                <p style="color: #666; font-size: 14px; margin-top: 8px;">
                    Find Your Inner Diva with AP Collection
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.form(key="login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("🚀 Login")

            if submitted:
                result = check_credentials(users, username, password)
                if result["valid"]:
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
        reset_session()
        st.rerun()

    process_list = [p_obj for p_name, p_obj in pages_process.items() if p_name in st.session_state["permissions"].keys()]
    report_list = [p_obj for p_name, p_obj in pages_report.items() if p_name in st.session_state["permissions"].keys()]

    if process_list or report_list:
        pg = st.navigation({
            "Process": process_list,
            "Report": report_list
        },)

        pg.run()
