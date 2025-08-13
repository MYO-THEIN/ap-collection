import streamlit as st
import pandas as pd
import math
from datetime import datetime, date, timedelta
from src.order import get_undelivered_orders, get_delivered_orders, get_order_items, update_delivery_status

st.set_page_config(layout="centered")
st.title("🚚 Delivery")

orders_per_page = 16
cols_per_row = 4
if "undelivered_page" not in st.session_state:
    st.session_state["undelivered_page"] = 1
if "last_search_term_undelivered" not in st.session_state:
    st.session_state["last_search_term_undelivered"] = None

@st.dialog(title="Order Info", width="large")
def display_order_info_dialog(id: int, date: date, order_no: str, customer_serial_no: str, customer_name: str, measurement: str):
    items = get_order_items(dt=None, order_ids=[str(id)])
    items = items[["stock_category_name", "description", "quantity"]]
    items.columns = ["Stock Category", "Description", "Quantity"]
    
    st.markdown(f"### {customer_serial_no} {customer_name}")
    st.markdown(order_no)
    st.dataframe(items)
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
    search_term_undelivered = st.text_input(
        label="🔎 Search Undelivered Order",
        max_chars=50
    )

    data_undelivered = get_undelivered_orders(search_term_undelivered if search_term_undelivered else None)

     # reset pagination if filter changes
    if (search_term_undelivered != st.session_state["last_search_term_undelivered"]):
        st.session_state["undelivered_page"] = 1
    st.session_state["last_search_term_undelivered"] = search_term_undelivered

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

                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("ℹ️", key=f"info_order_{rows.iloc[j]['id']}", use_container_width=True):
                            display_order_info_dialog(
                                id=rows.iloc[j]["id"],
                                date=rows.iloc[j]["date"],
                                order_no=rows.iloc[j]["order_no"],
                                customer_serial_no=rows.iloc[j]["customer_serial_no"],
                                customer_name=rows.iloc[j]["customer_name"],
                                measurement=rows.iloc[j]['measurement']
                            )
                    with btn_col2:
                        if st.button("🚛", key=f"deliver_{rows.iloc[j]['id']}_{i}", use_container_width=True):
                            success = update_delivery_status(
                                id=int(rows.iloc[j]["id"]),
                                is_delivered=True,
                                delivery_date=datetime.now().strftime("%Y-%m-%d")
                            )

                            if success:
                                st.session_state["show_success"] = True
                                st.session_state["show_success_msg"] = "Order has been delivered."
                            else:
                                st.session_state["show_error"] = True
                                st.session_state["show_error_msg"] = "Delivering an order has failed due to some errors."
                            st.rerun()
    else:
        st.info("No data available 📭")

with tab2:
    data_delivered = pd.DataFrame()
    filter_mode = st.radio(label="🔎 Search Delivered Order", options=["Date", "Customer"], horizontal=True)
    if filter_mode == "Date":
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
        
    elif filter_mode == "Customer":
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
