import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta
from src.order import get_undelivered_orders, get_delivered_orders, get_order_items, get_order_by_id, update_delivery_status
from src.utils import confirmation_dialog, build_receipt_html
from streamlit.components.v1 import html

st.set_page_config(layout="centered")

# Authorization
if ("authenticated" not in st.session_state) or ("authenticated" in st.session_state and st.session_state["authenticated"] == False):
    st.session_state.clear()
    st.rerun()
else:
    user_name, role_name = st.session_state["user_name"], st.session_state["role_name"]
    permissions = st.session_state["permissions"]

    if "Delivery" in permissions.keys():
        deliver_permission = permissions["Delivery"]["deliver"]
        receipt_permission = permissions["Delivery"]["receipt"]

st.title("🚚 Delivery")

orders_per_page = 16
cols_per_row = 4
if "undelivered_page" not in st.session_state:
    st.session_state["undelivered_page"] = 1
if "last_filter_mode_undelivered" not in st.session_state:
    st.session_state["last_filter_mode_undelivered"] = None
if "last_filter_value_undelivered" not in st.session_state:
    st.session_state["last_filter_value_undelivered"] = None

@st.dialog(title="Order Info", width="large")
def display_order_info_dialog(id: int, date: date, order_no: str, customer_serial_no: str, customer_name: str, measurement: str):
    items = get_order_items(dt=None, order_ids=[str(id)])
    items = items[["stock_category_name", "description", "quantity"]]
    items.columns = ["Stock Category", "Description", "Quantity"]
    
    st.markdown(f"### {customer_serial_no} {customer_name}")
    st.markdown(order_no)
    st.dataframe(items)
    if measurement is not None and measurement.strip() != "":
        st.markdown("Measurement")
        st.markdown(measurement.replace("\n", "<br>"), unsafe_allow_html=True)

# CSS for cards
st.markdown("""
    <style>
    .order-card {
        border: 2px solid orange;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
        height: 150px;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

if "show_success" in st.session_state and st.session_state["show_success"]:
    st.success(st.session_state["show_success_msg"], icon=":material/thumb_up:")
    del st.session_state["show_success"]
    del st.session_state["show_success_msg"]
elif "show_error" in st.session_state and st.session_state["show_error"]:
    st.error(st.session_state["show_error_msg"], icon=":material/thumb_down:")
    del st.session_state["show_error"]
    del st.session_state["show_error_msg"]

tab1, tab2 = st.tabs(["🚚 Undelivered", "🚛 Delivered"])
with tab1:
    data_undelivered = pd.DataFrame()
    filter_mode_undelivered = st.radio(label="🔎 Search Undelivered Order", options=["Due Date", "Order Date", "Customer"], horizontal=True)
    # Due Date filter
    if filter_mode_undelivered == "Due Date":
        due_date_undelivered = st.date_input(
            label="Due Date", label_visibility="collapsed", 
            value=datetime.today(), format="YYYY-MM-DD", 
            key="search_due_date_undelivered"
        )
        filter_value_undelivered = str(due_date_undelivered)
        if due_date_undelivered:
            data_undelivered = get_undelivered_orders(due_date=due_date_undelivered)
    
    # Order Date filter
    elif filter_mode_undelivered == "Order Date":
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            order_date_from_undelivered = st.date_input(
                label="From", label_visibility="collapsed", 
                value=datetime.today() - timedelta(days=6), format="YYYY-MM-DD", 
                key="search_order_date_from_undelivered"
            )
        with date_col2:
            order_date_to_undelivered = st.date_input(
                label="To", label_visibility="collapsed", 
                value=datetime.today(), format="YYYY-MM-DD", 
                key="search_order_date_to_undelivered"
            )
        filter_value_undelivered = f"{str(order_date_from_undelivered)} to {str(order_date_to_undelivered)}"
        if order_date_from_undelivered and order_date_to_undelivered:
            data_undelivered = get_undelivered_orders(
                due_date=None, 
                order_date_from=order_date_from_undelivered,
                order_date_to=order_date_to_undelivered 
            )
    
    # Customer filter
    elif filter_mode_undelivered == "Customer":
        search_term_undelivered = st.text_input(
            label="🔎 Search Undelivered Order", 
            label_visibility="collapsed",
            max_chars=50
        )
        filter_value_undelivered = search_term_undelivered
        data_undelivered = get_undelivered_orders(
            due_date=None,
            order_date_from=None, 
            order_date_to=None,
            search_term=search_term_undelivered if search_term_undelivered else None
        )

    # reset pagination if filter changes
    if (filter_mode_undelivered != st.session_state["last_filter_mode_undelivered"] or filter_value_undelivered != st.session_state["last_filter_value_undelivered"]):
        st.session_state["undelivered_page"] = 1
    st.session_state["last_filter_mode_undelivered"] = filter_mode_undelivered
    st.session_state["last_filter_value_undelivered"] = filter_value_undelivered

    st.write("### Undelivered Orders")
    if data_undelivered.shape[0]:
        # pagination
        total_pages = (len(data_undelivered) - 1) // orders_per_page + 1
        col1, col2, col3 = st.columns([1, 3, 1], vertical_alignment="center")
        with col1:
            if st.button("⬅ Prev", use_container_width=True) and st.session_state["undelivered_page"] > 1:
                st.session_state["undelivered_page"] = st.session_state["undelivered_page"] - 1
        with col3:
            if st.button("Next ➡", use_container_width=True) and st.session_state["undelivered_page"] < total_pages:
                st.session_state["undelivered_page"] = st.session_state["undelivered_page"] + 1  
        with col2:
            st.markdown(
                f"<div style='text-align: center;'>Page {st.session_state['undelivered_page']} of {total_pages}</div>",
                unsafe_allow_html=True
            )

        start = (st.session_state["undelivered_page"] - 1) * orders_per_page
        end = start + orders_per_page
        paginated_data = data_undelivered[start : end]

        for i in range(0, len(paginated_data), cols_per_row):
            cols = st.columns(cols_per_row)
            rows = paginated_data[i : i + cols_per_row]

            for j in range(cols_per_row):
                if (j + 1) > len(rows):
                    break

                with cols[j]:
                    due_date_fmt = rows.iloc[j]["delivery_date"].strftime("%m-%d")
                    order_date_fmt = rows.iloc[j]["date"].strftime("%m-%d")
                    st.markdown(
                        f"""
                        <div class="order-card">
                            <b>Due Date:</b> {due_date_fmt}<br>
                            <b>Order Date:</b> {order_date_fmt}<br>
                            <b>Serial No:</b> {rows.iloc[j]['customer_serial_no']}<br>
                            <b>Name:</b> {rows.iloc[j]['customer_name']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    btn_col1, btn_col2, btn_col3 = st.columns(3)
                    # Order Info Button
                    with btn_col1:
                        if st.button("ℹ️", help="Order Info", key=f"info_order_{rows.iloc[j]['id']}", use_container_width=True):
                            display_order_info_dialog(
                                id=rows.iloc[j]["id"],
                                date=rows.iloc[j]["date"],
                                order_no=rows.iloc[j]["order_no"],
                                customer_serial_no=rows.iloc[j]["customer_serial_no"],
                                customer_name=rows.iloc[j]["customer_name"],
                                measurement=rows.iloc[j]['measurement']
                            )
                    # Deliver Button
                    with btn_col2:
                        if st.button("🚛", help="Deliver", key=f"deliver_{rows.iloc[j]['id']}_{i}", use_container_width=True, disabled=not deliver_permission):
                            st.session_state["to_deliver_order_id"] = rows.iloc[j]["id"]
                            confirmation_dialog(
                                msg="Are you sure to deliver this order?", 
                                yes_button_txt="✅ Yes, deliver", 
                                no_button_txt="❌ Cancel"
                            )
                    # Receipt Button
                    with btn_col3:
                        if st.button("🖨️", help="Print Receipt", key=f"receipt_{rows.iloc[j]['id']}_{i}", use_container_width=True, disabled=not receipt_permission):
                            order = get_order_by_id(id=int(rows.iloc[j]["id"]))
                            items = get_order_items(dt=None, order_ids=[int(rows.iloc[j]["id"])])
                            receipt_html = build_receipt_html(order=order.iloc[0], items=items.to_dict(orient="records"))
                            html(receipt_html, height=0, width=0)
    else:
        st.info("No data available 📭")

with tab2:
    data_delivered = pd.DataFrame()
    filter_mode_delivered = st.radio(label="🔎 Search Delivered Order", options=["Date", "Customer"], horizontal=True)
    # Date filter 
    if filter_mode_delivered == "Date":
        date_col1, date_col2 = st.columns(2)
        with date_col1:
            from_date_delivered = st.date_input(
                label="From", label_visibility="collapsed", 
                value=datetime.today(), format="YYYY-MM-DD", 
                key="search_from_date_delivered"
            )
        with date_col2:
            to_date_delivered = st.date_input(
                label="To", label_visibility="collapsed", 
                value=datetime.today(), format="YYYY-MM-DD", 
                key="search_to_date_delivered"
            )
        if from_date_delivered and to_date_delivered:
            data_delivered = get_delivered_orders(from_date_delivered, to_date_delivered, search_term=None)
    
    # Customer filter
    elif filter_mode_delivered == "Customer":
        search_term_delivered = st.text_input(label="Search", label_visibility="collapsed")
        if search_term_delivered:
            data_delivered = get_delivered_orders(from_date=None, to_date=None, search_term=search_term_delivered)
    
    st.write("### Delivered Orders")
    if data_delivered.shape[0]:
        data_delivered.columns = [
            "Delivery Date", "Order Date", "Order No.", "Serial No.", "Name", 
            "Stock Category", "Description", "Quantity"
        ]
        st.dataframe(data_delivered, use_container_width=True)
    else:
        st.info("No data available 📭")


# Order confirmed and good to go 
if "confirmed_action" in st.session_state:
    if st.session_state["confirmed_action"] == True and "to_deliver_order_id" in st.session_state:
        success = update_delivery_status(
            id=int(st.session_state["to_deliver_order_id"]),
            is_delivered=True,
            delivery_date=datetime.now().strftime("%Y-%m-%d")
        )

        if success:
            st.session_state["show_success"] = True
            st.session_state["show_success_msg"] = "Order has been delivered."
            del st.session_state["confirmed_action"]
            del st.session_state["to_deliver_order_id"]
        else:
            st.session_state["show_error"] = True
            st.session_state["show_error_msg"] = "Delivering an order has failed due to some errors."
        st.rerun()
