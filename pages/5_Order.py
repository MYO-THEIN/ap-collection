import streamlit as st
import pandas as pd
from datetime import datetime 
import src.order as controller
import forms.order as order_form
import src.utils as utils
from streamlit.components.v1 import html

st.set_page_config(layout="centered")

# Authorization
if st.session_state["authenticated"] == False:
    st.session_state.clear()
    st.rerun()
else:
    user_name, role_name = st.session_state["user_name"], st.session_state["role_name"]
    permissions = st.session_state["permissions"]

    if "Order" in permissions.keys():
        new_permission = permissions["Order"]["new"]
        edit_permission = permissions["Order"]["edit"]
        delete_permission = permissions["Order"]["delete"]
        receipt_permission = permissions["Order"]["receipt"]

st.title("🛒 Orders")

if "show_form" not in st.session_state:
    st.session_state["show_form"] = False

trans_per_page = 5
if "page" not in st.session_state:
    st.session_state["page"] = 1
if "last_filter_mode" not in st.session_state:
    st.session_state["last_filter_mode"] = None
if "last_filter_value" not in st.session_state:
    st.session_state["last_filter_value"] = None

# Search
with st.spinner("Searching ..."):
    data, data_items = pd.DataFrame(), pd.DataFrame()
    filter_mode = st.radio(label="🔎 Search Order", options=["Date", "Customer"], horizontal=True)
    if filter_mode == "Date":
        dt = st.date_input(label="Date", label_visibility="collapsed", value=datetime.today(), format="YYYY-MM-DD", key="search_date")
        filter_value = str(dt)
        if dt:
            data = controller.get_orders(dt=dt, search_term=None)
            if data is not None and len(data["id"].tolist()):
                data_items = controller.get_order_items(dt=dt, order_ids=data["id"].tolist())

    elif filter_mode == "Customer":
        search_term = st.text_input(label="Search Order", label_visibility="collapsed")
        filter_value = search_term
        if search_term:
            data = controller.get_orders(dt=None, search_term=search_term)
            if data is not None and len(data["id"].tolist()):
                data_items = controller.get_order_items(dt=None, order_ids=data["id"].tolist())

    # reset pagination if filter changes
    if (filter_mode != st.session_state["last_filter_mode"] or filter_value != st.session_state["last_filter_value"]):
        st.session_state["page"] = 1
    st.session_state["last_filter_mode"] = filter_mode
    st.session_state["last_filter_value"] = filter_value

    st.write("### Orders")
    if data.shape[0]:
        # pagination
        total_pages = (len(data) - 1) // trans_per_page + 1
        col1, col2, col3 = st.columns([1, 3, 1], vertical_alignment="center")
        with col1:
            if st.button("⬅ Prev", use_container_width=True) and st.session_state["page"] > 1:
                st.session_state["page"] = st.session_state["page"] - 1
        with col3:
            if st.button("Next ➡", use_container_width=True) and st.session_state["page"] < total_pages:
                st.session_state["page"] = st.session_state["page"] + 1  
        with col2:
            st.markdown(
                f"<div style='text-align: center;'>Page {st.session_state['page']} of {total_pages}</div>",
                unsafe_allow_html=True
            )

        start = (st.session_state["page"] - 1) * trans_per_page
        end = start + trans_per_page
        paginated_data = data[start : end]

        for _, row in paginated_data.iterrows():
            items = data_items[data_items["order_id"] == row["id"]]

            col1, col2 = st.columns([3, 1], vertical_alignment="center")
            with col1:
                if row["is_delivered"]:
                    st.markdown(f"# :green-badge[:truck: Delivered: {row['delivery_date']}]")
                else:
                    st.markdown(f"# :orange-badge[:bulb: Due: {row['delivery_date']}]")

                st.markdown(f"**Date**: {row['date']} | **Customer**: {row['customer_serial_no']} {row['customer_name']} | **Total Quantity**: {row['ttl_quantity']}")
                st.markdown(f"**Total Amount**: {row['ttl_amount']:,} | **Discount**: {row['discount']:,} | **Delivery Charges**: {row['delivery_charges']:,}")
                st.markdown(f"**Payment Type**: {row['payment_type_name']} | **Paid Amount**: {row['paid_amount']:,}")
            
            with col2:
                col_edit, col_delete, col_receipt = st.columns(3)
                
                # Edit Button
                with col_edit:
                    if st.button(label="✏️", help="Edit Order", key=f"edit_{row['id']}", use_container_width=True, disabled=not edit_permission):
                        st.session_state["edit_id"] = row["id"]
                        st.session_state["edit_date"] = row["date"]
                        st.session_state["edit_order_no"] = row["order_no"]                        
                        st.session_state["search_id"] = row["customer_id"]
                        st.session_state["search_serial_no"] = row["customer_serial_no"]
                        st.session_state["search_name"] = row["customer_name"]
                        st.session_state["search_phone"] = row["customer_phone"]
                        st.session_state["search_delivery_address"] = row["customer_delivery_address"]
                        st.session_state["search_city"] = row["customer_city"]
                        st.session_state["search_state_region"] = row["customer_state_region"]
                        st.session_state["edit_customer_id"] = row["customer_id"]
                        st.session_state["edit_delivery_address"] = row["delivery_address"]
                        st.session_state["edit_ttl_quantity"] = row["ttl_quantity"]
                        st.session_state["edit_ttl_amount"] = row["ttl_amount"]
                        st.session_state["edit_discount"] = row["discount"]
                        st.session_state["edit_sub_total"] = row["sub_total"]
                        st.session_state["edit_delivery_charges"] = row["delivery_charges"]
                        st.session_state["edit_payment_type_id"] = row["payment_type_id"]
                        st.session_state["edit_payment_type_name"] = row["payment_type_name"]
                        st.session_state["edit_paid_amount"] = row["paid_amount"]
                        st.session_state["edit_measurement"] = row["measurement"]
                        st.session_state["edit_is_delivered"] = row["is_delivered"]
                        st.session_state["edit_delivery_date"] = row["delivery_date"]
                        st.session_state["edit_order_items"] = items.drop(columns=["id", "order_id"]).to_dict(orient="records")

                # Delete Button
                with col_delete:
                    if st.button(label="🗑️", help="Delete Order", key=f"delete_{row['id']}", use_container_width=True, disabled=not delete_permission):
                        st.session_state["to_delete_order_id"] = row["id"]
                        utils.confirmation_dialog(
                            msg="Are you sure to delete this order?", 
                            yes_button_txt="✅ Yes, delete", 
                            no_button_txt="❌ Cancel"
                        )

                # Receipt Button
                with col_receipt:
                    if st.button(label="🖨️", help="Print Receipt", key=f"receipt_{row['id']}", use_container_width=True, disabled=not receipt_permission):
                        receipt_html = utils.build_receipt_html(order=row.to_dict(), items=items.to_dict(orient="records"))
                        html(receipt_html, height=0, width=0)


            with st.expander(label="📋 Items"):
                items = items.drop(columns=["id", "order_id", "stock_category_id"])
                items = items.style.format({
                    "price": "{:,.0f}",
                    "extra": "{:,.0f}",
                    "amount": "{:,.0f}"
                })

                st.dataframe(
                    data=items,
                    column_config={
                        "stock_category_name": st.column_config.Column(label="Stock Category", disabled=True),
                        "description": st.column_config.Column(label="Description", disabled=True),
                        "quantity": st.column_config.Column(label="Quantity", disabled=True),
                        "price": st.column_config.Column(label="Price", disabled=True),
                        "extra": st.column_config.Column(label="Extra", disabled=True),
                        "amount": st.column_config.Column(label="Amount", disabled=True)
                    },
                    hide_index=True
                )

                if row["measurement"]:
                    st.markdown("Measurement")
                    st.markdown(row["measurement"].replace("\n", "<br>"), unsafe_allow_html=True)

            st.divider()
    else:
        st.info("No data available 📭")
        st.divider()


def clear_all_inputs():
    # Add New
    add_new_keys = [
        "date", "order_no",
        "search_id", "search_serial_no", "search_name", "search_phone", "search_delivery_address", "search_city", "search_state_region", 
        "delivery_address", "ttl_quantity", "ttl_amount", "discount", "sub_total", "delivery_charges", "payment_type_id", "payment_type_name", "paid_amount",
        "measurement", "is_delivered", "delivery_date"
    ]
    for key in add_new_keys:
        if key in st.session_state:
            del st.session_state[key]

    # Edit
    edit_keys = [
        "edit_id", "edit_date", "edit_order_no", 
        "search_id", "search_serial_no", "search_name", "search_phone", "search_delivery_address", "search_city", "search_state_region", 
        "edit_customer_id", "edit_delivery_address", "edit_ttl_quantity", "edit_ttl_amount", "edit_discount", "edit_sub_total", "edit_delivery_charges", "edit_payment_type_id", "edit_payment_type_name", "edit_paid_amount",
        "edit_measurement", "edit_is_delivered", "edit_delivery_date",
        "edit_order_items"
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]

def order_form_callback(data=None):
    if "show_success" in data:
        st.session_state["show_success"] = data["show_success"]
        st.session_state["show_success_msg"] = data["show_success_msg"]
    elif "show_error" in data:
        st.session_state["show_error"] = data["show_error"]
        st.session_state["show_error_msg"] = data["show_error_msg"]

    clear_all_inputs()
    st.session_state["show_form"] = False
    st.rerun()

# Add New Form
if new_permission:
    if st.button("➕ Add New Order"):
        clear_all_inputs()
        st.session_state["show_form"] = True

# Edit Form
if "edit_id" in st.session_state:
    st.session_state["show_form"] = True

if st.session_state["show_form"]:
    order_form.order_form(is_edit="edit_id" in st.session_state, submit_callback=order_form_callback)

if "show_success" in st.session_state and st.session_state["show_success"]:
    st.success(st.session_state["show_success_msg"], icon=":material/thumb_up:")
    del st.session_state["show_success"]
    del st.session_state["show_success_msg"]
elif "show_error" in st.session_state and st.session_state["show_error"]:
    st.error(st.session_state["show_error_msg"], icon=":material/thumb_down:")
    del st.session_state["show_error"]
    del st.session_state["show_error_msg"]

# Delete confirmed and good to go 
if "confirmed_action" in st.session_state:
    if st.session_state["confirmed_action"] == True and "to_delete_order_id" in st.session_state:
        success = controller.delete_order(st.session_state["to_delete_order_id"])

        if success:
            st.session_state["show_success"] = True
            st.session_state["show_success_msg"] = "Deleted successfully."
            del st.session_state["confirmed_action"]
            del st.session_state["to_delete_order_id"]
        else:
            st.session_state["show_error"] = True
            st.session_state["show_error_msg"] = "Deleting an order has failed due to some errors."
        st.rerun()
