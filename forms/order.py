import streamlit as st
import pandas as pd
from datetime import datetime, date
import forms.search_customer as search_customer
from src.payment_type import get_payment_types
from src.stock_category import get_stock_categories
import src.order as controller

if "order_items" not in st.session_state:
    st.session_state["order_items"] = []

@st.cache_data
def load_payment_types():
    return get_payment_types()

@st.cache_data
def load_stock_categories():
    return get_stock_categories()

payment_types = load_payment_types()
stock_categories = load_stock_categories()


def construct_order_no(dt: date, customer_serial_no: str):
    return f"{dt}-{datetime.now.strftime("%H%M%S")}-{customer_serial_no}"


def order_form(is_edit: bool, submit_callback=None):
    col1, col2 = st.columns(2)

    # ----- Order Info -----
    with col1:
        st.subheader("Order Info")

        dt = st.date_input(
            label="Date", 
            value=datetime.today(),
            format="YYYY-MM-DD"
        )

        left, right = st.columns(2, vertical_alignment="bottom")
        search_customer_submit = left.button("🔎 Customer", use_container_width=True)
        if search_customer_submit:
            search_customer.search_customer_modal(
                sel_id=st.session_state["search_id"] if "search_id" in st.session_state else None,
                sel_serial_no=st.session_state["search_serial_no"] if "search_serial_no" in st.session_state else None,
                sel_name=st.session_state["search_name"] if "search_name" in st.session_state else None,
                sel_phone=st.session_state["search_phone"] if "search_phone" in st.session_state else None,
                sel_delivery_address=st.session_state["search_delivery_address"] if "search_delivery_address" in st.session_state else None,
                sel_city=st.session_state["search_city"] if "search_city" in st.session_state else None,
                sel_state_region=st.session_state["search_state_region"] if "search_state_region" in st.session_state else None
            )
        serial_no = right.text_input(
            label="Serial No.",
            value=st.session_state["search_serial_no"] if "search_serial_no" in st.session_state else "",
            disabled=True,
            label_visibility="collapsed"
        )

        name = st.text_input(
            label="Name",
            value=st.session_state["search_name"] if "search_name" in st.session_state else "",
            disabled=True
        )

        phone = st.text_input(
            label="Phone",
            value=st.session_state['search_phone'] if 'search_phone' in st.session_state else "",
            disabled=True
        )

        searched_delivery_address = st.session_state["search_delivery_address"] if "search_delivery_address" in st.session_state else ""
        searched_city = st.session_state["search_city"] if "search_city" in st.session_state else ""
        searched_state_region = st.session_state["search_state_region"] if "search_state_region" in st.session_state else ""
        delivery_address = st.text_area(
            label="Delivery Address",
            value=searched_delivery_address + searched_city + searched_state_region,
            max_chars=200
        )

        delivery_charges = st.number_input(
            label="Delivery Charges",
            min_value=0, 
            max_value=10000,
            value=0
        )

        payment_type_name = st.selectbox(
            label="Payment Type",
            options=payment_types["name"].tolist(),
            accept_new_options=False
        )
        if payment_type_name:
            payment_type_id = payment_types[payment_types["name"] == payment_type_name].iloc[0]["id"]

    # ----- Item Info -----
    with col2:
        st.subheader("Item Info")

        with st.form(key="add_new_item_form" if is_edit else "edit_item_form", clear_on_submit=True):
            stock_category_name = st.selectbox(
                label="Stock Category",
                options=stock_categories["name"].tolist(),
                accept_new_options=False
            )
            if stock_category_name:
                stock_category_id = stock_categories[stock_categories["name"] == stock_category_name].iloc[0]["id"]

            quantity = st.number_input("Quantity", min_value=1, value=1, format="%d")
            amount = st.number_input("Amount", min_value=0, format="%d")

            add_detail = st.form_submit_button("Add Item")
            if add_detail:
                if stock_category_name and quantity and amount:
                    detail = {
                        "stock_category_id": stock_category_id,
                        "stock_category_name": stock_category_name,
                        "quantity": quantity,
                        "amount": amount
                    }
                    st.session_state["order_items"].append(detail)
                    st.success(f"Added: {stock_category_name} x {quantity}")

    # ----- Items List -----
    st.subheader("📋 Order Items")
    if st.session_state["order_items"]:
        st.dataframe(st.session_state["order_items"], use_container_width=True)
    else:
        st.info("No items added yet.")

    ttl_quantity, ttl_amount = 0, 0
    for d in st.session_state["order_items"]:
        ttl_quantity += d["quantity"]
        ttl_amount += d["amount"]
    st.markdown(f"### 🧮 Total Quantity: {ttl_quantity}")
    st.markdown(f"### 🧮 Total Amount: {ttl_amount :,}")

    if st.button("✅ Confirm Order" if not is_edit else "Save Order"):
        if "search_id" not in st.session_state:
            st.warning("Select a customer.")
        elif delivery_address is None:
            st.warning("Enter the delivery address.")
        elif payment_type_id is None:
            st.warning("Select a payment type.")
        elif len(st.session_state["order_items"]) == 0:
            st.warning("Order must have an item at least.")            
        else:
            order = {
                "id": st.session_state["edit_id"] if is_edit else None,
                "date": dt,
                "order_no": construct_order_no(date, serial_no),
                "customer_id": st.session_state["search_id"],
                "ttl_quantity": ttl_quantity,
                "ttl_amount": ttl_amount,
                "discount": 0,
                "sub_total": ttl_amount,
                "delivery_address": delivery_address,
                "delivery_charges": delivery_charges,
                "payment_type_id": payment_type_id
            }

            if is_edit:
                success = controller.update_order(order=order, order_items=st.session_state["order_items"])
                msg = "Updated successfully."
            else:
                success = controller.add_order(order=order, order_items=st.session_state["order_items"])
                msg = "Added successfully."

            if success:
                del st.session_state["order_items"]
                st.session_state["show_success"] = True
                st.session_state["show_success_message"] = msg
                if submit_callback:
                    submit_callback({
                        "show_success": True,
                        "show_success_msg": msg
                    })
