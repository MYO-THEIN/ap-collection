import streamlit as st
import pandas as pd
from datetime import datetime, date
from forms import customer, search_customer
from src.payment_type import get_payment_types
from src.stock_category import get_stock_categories
from src.customer import get_customer_by_id
import src.order as controller

if "order_items" not in st.session_state:
    st.session_state["order_items"] = []

@st.dialog(title="Add New Customer", width="large")
def display_customer_form_dialog():
    customer.customer_form(is_edit=False, submit_callback=new_customer_submit_callback)

def new_customer_submit_callback(data=None):
    if "show_success" in data:
        df = get_customer_by_id(id=data["new_id"])
        if df.shape[0]:
            st.session_state["search_id"] = int(df.iloc[0]["id"])
            st.session_state["search_serial_no"] = df.iloc[0]["serial_no"]
            st.session_state["search_name"] = df.iloc[0]["name"]
            st.session_state["search_phone"] = df.iloc[0]["phone"]
            st.session_state["search_delivery_address"] = df.iloc[0]["delivery_address"]
            st.session_state["search_city"] = df.iloc[0]["city"]
            st.session_state["search_state_region"] = df.iloc[0]["state_region"]
            st.rerun()

if "payment_types" in st.session_state:
    del st.session_state["payment_types"]
if "stock_categories" in st.session_state:
    del st.session_state["stock_categories"]
payment_types = get_payment_types()
stock_categories = get_stock_categories()

def construct_order_no(dt: date, customer_serial_no: str):
    return f"{dt.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}-{customer_serial_no}"

def order_form(is_edit: bool, submit_callback=None):
    col1, col2 = st.columns(2)

    # ----- Order Info -----
    with col1:
        st.subheader("🧾 Order Info")

        dt = st.date_input(
            label="Date", 
            value=datetime.today() if not is_edit else st.session_state["edit_date"],
            format="YYYY-MM-DD"
        )

        if is_edit:
            edit_order_no = st.text_input(
                label="Order No.",
                value=st.session_state["edit_order_no"],
                disabled=True
            )

        left, right = st.columns(2, vertical_alignment="bottom")
        left1, left2 = left.columns(2, vertical_alignment="bottom")
        # Search Customer
        with left1:
            search_customer_submit = st.button("🔎", use_container_width=True)
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
        # New Customer
        with left2:
            new_customer_submit = st.button("➕", use_container_width=True)
            if new_customer_submit:
                display_customer_form_dialog()
                    
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
        if is_edit:
            if st.session_state["search_id"] == st.session_state["edit_customer_id"]:
                deli_addr = st.session_state["edit_delivery_address"]
            else:
                deli_addr = f"{searched_delivery_address}, {searched_city}, {searched_state_region}"
        else:
            deli_addr = f"{searched_delivery_address}, {searched_city}, {searched_state_region}"
        delivery_address = st.text_area(
            label="Delivery Address",
            value=deli_addr,
            max_chars=200
        )

        delivery_charges = st.number_input(
            label="Delivery Charges",
            min_value=0, 
            max_value=10000,
            value=st.session_state["edit_delivery_charges"] if is_edit else 0
        )

        payment_type_name = st.selectbox(
            label="Payment Type",
            options=payment_types["name"].tolist(),
            accept_new_options=False,
            index=payment_types["name"].tolist().index(st.session_state["edit_payment_type_name"]) if is_edit else payment_types["name"].tolist().index("KBZ Pay")
        )
        if payment_type_name:
            payment_type_id = int(payment_types[payment_types["name"] == payment_type_name].iloc[0]["id"])

    # ----- Item Info -----
    with col2:
        st.subheader("🏷️ Item Info")

        with st.form(key="add_new_item_form" if is_edit else "edit_item_form", clear_on_submit=True):
            stock_category_name = st.selectbox(
                label="Stock Category",
                options=stock_categories["name"].tolist(),
                accept_new_options=False
            )
            if stock_category_name:
                stock_category_id = int(stock_categories[stock_categories["name"] == stock_category_name].iloc[0]["id"])

            quantity = st.number_input("Quantity", min_value=1, value=1, format="%d")
            amount = st.number_input("Amount", min_value=0, format="%d")

            add_detail = st.form_submit_button("Add Item")
            if add_detail:
                if stock_category_name and quantity and amount:
                    item = {
                        "stock_category_id": stock_category_id,
                        "stock_category_name": stock_category_name,
                        "quantity": quantity,
                        "amount": amount
                    }

                    if is_edit:
                        st.session_state["edit_order_items"].append(item)
                    else:
                        if "order_items" not in st.session_state:
                            st.session_state["order_items"] = []
                        st.session_state["order_items"].append(item)

                    st.success(f"Added: {stock_category_name} x {quantity}")

    # ----- Items List -----
    st.subheader("📋 Order Items")
    if ("order_items" in st.session_state and st.session_state["order_items"]) or ("edit_order_items" in st.session_state and st.session_state["edit_order_items"]):
        df = st.data_editor(
            data=st.session_state["order_items"] if not is_edit else st.session_state["edit_order_items"],
            column_config={
                "stock_category_id": st.column_config.Column(label="Stock Category ID", disabled=True),
                "stock_category_name": st.column_config.Column(label="Stock Category", disabled=True),
                "quantity": st.column_config.NumberColumn(label="Quantity", step="1"),
                "amount": st.column_config.NumberColumn(label="Amount", step="1000")
            },
            use_container_width=True,
            num_rows="dynamic",
            hide_index=False,
            key="order_items_data_editor"
        )

        if is_edit:
            st.session_state["edit_order_items"] = df
        else:
            st.session_state["order_items"] = df
    else:
        st.info("No items added yet.")

    ttl_quantity, ttl_amount = 0, 0
    if is_edit and "edit_order_items" in st.session_state:
        for d in st.session_state["edit_order_items"]:
            ttl_quantity += d["quantity"]
            ttl_amount += d["amount"]
    elif not is_edit and "order_items" in st.session_state:
        for d in st.session_state["order_items"]:
            ttl_quantity += d["quantity"]
            ttl_amount += d["amount"]
    st.markdown(f"### 🧮 Total Quantity: {ttl_quantity:,}")
    st.markdown(f"### 🧮 Total Amount: {ttl_amount:,}")
    paid_amount = st.number_input(
        label="Paid Amount",
        value=st.session_state["edit_paid_amount"] if is_edit else (ttl_amount + delivery_charges)
    )

    # Save
    if st.button("✅ Confirm Order" if not is_edit else "💾 Save Order"):
        if "search_id" not in st.session_state:
            st.warning("Select a customer.")
        elif delivery_address is None:
            st.warning("Enter the delivery address.")
        elif payment_type_id is None:
            st.warning("Select a payment type.")
        elif not is_edit and not st.session_state["order_items"]:
            st.warning("Order must have an item at least.")
        elif is_edit and not st.session_state["edit_order_items"]:
            st.warning("Order must have an item at least.")
        else:
            order = {
                "id": st.session_state["edit_id"] if is_edit else None,
                "date": dt,
                "order_no": construct_order_no(dt, serial_no) if not is_edit else edit_order_no,
                "customer_id": st.session_state["search_id"],
                "ttl_quantity": ttl_quantity,
                "ttl_amount": ttl_amount,
                "discount": 0,
                "sub_total": ttl_amount,
                "delivery_address": delivery_address,
                "delivery_charges": delivery_charges,
                "payment_type_id": payment_type_id,
                "paid_amount": paid_amount
            }

            if is_edit:
                success = controller.update_order(order=order, order_items=st.session_state["edit_order_items"])
                msg = "Updated successfully." if success else "Updating an order failed."
            else:
                success = controller.add_order(order=order, order_items=st.session_state["order_items"])
                msg = "Added successfully." if success else "Adding an order failed."

            if success:
                if "order_items" in st.session_state: 
                    del st.session_state["order_items"]
                if "edit_order_items" in st.session_state:
                    del st.session_state["edit_order_items"]
                st.session_state["show_success"] = True
                st.session_state["show_success_message"] = msg
                if submit_callback:
                    submit_callback({
                        "show_success": True,
                        "show_success_msg": msg
                    })
            else:
                submit_callback({
                    "show_error": True,
                    "show_error_msg": msg
                })
