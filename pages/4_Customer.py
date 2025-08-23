import streamlit as st
import pandas as pd
import src.customer as controller
import forms.customer as customer_form
from src.utils import confirmation_dialog

st.set_page_config(layout="centered")

# Authorization
if st.session_state["authenticated"] == False:
    st.session_state.clear()
    st.rerun()
else:
    user_name, role_name = st.session_state["user_name"], st.session_state["role_name"]
    permissions = st.session_state["permissions"]

    if "Customer" in permissions.keys():
        new_permission = permissions["Customer"]["new"]
        edit_permission = permissions["Customer"]["edit"]
        delete_permission = permissions["Customer"]["delete"]

st.title("🧑 Customers")

if "show_form" not in st.session_state:
    st.session_state["show_form"] = False

trans_per_page = 20
if "page" not in st.session_state:
    st.session_state["page"] = 1
if "last_filter_value" not in st.session_state:
    st.session_state["last_filter_value"] = None

# Search
with st.spinner("Searching ..."):
    search_term = st.text_input("🔍 Search Customer")
    data = controller.get_customers(search_term)

    # reset pagination if filter changes
    if (search_term != st.session_state["last_filter_value"]):
        st.session_state["page"] = 1
    st.session_state["last_filter_value"] = search_term

    st.write("### Customers")
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

        for idx, row in paginated_data.iterrows():
            cols = st.columns([1, 1, 1, 1, 1, 1])
            cols[0].write(f"**{row['serial_no']}**")
            cols[1].write(f"**{row['name']}**")
            cols[2].write(row['city'])
            cols[3].write(row['country'])

            if cols[4].button("✏️ Edit", key=f"edit_{row['id']}", use_container_width=True, disabled=not edit_permission):
                st.session_state["edit_id"] = row["id"]
                st.session_state["edit_serial_no"] = row["serial_no"]
                st.session_state["edit_name"] = row["name"]
                st.session_state["edit_phone"] = row["phone"]
                st.session_state["edit_home_address"] = row["home_address"]
                st.session_state["edit_delivery_address"] = row["delivery_address"]
                st.session_state["edit_city"] = row["city"]
                st.session_state["edit_state_region"] = row["state_region"]
                st.session_state["edit_country"] = row["country"]

            if cols[5].button("🗑️ Delete", key=f"delete_{row['id']}", use_container_width=True, disabled=not delete_permission):
                st.session_state["to_delete_customer_id"] = row["id"]
                confirmation_dialog(
                    msg="Are you sure to delete this customer?", 
                    yes_button_txt="✅ Yes, delete", 
                    no_button_txt="❌ Cancel"
                )
    else:
        st.write("No data available 📭")

st.divider()


def clear_all_inputs():
    keys = ["id", "serial_no", "name", "phone", "home_address", "delivery_address", "city", "state_region", "country"]
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]
        if f"edit_{key}" in st.session_state:
            del st.session_state[f"edit_{key}"]

def customer_form_callback(data=None):
    if "show_success" in data:
        st.session_state["show_success"] = data["show_success"]
        st.session_state["show_success_msg"] = data["show_success_msg"]
        clear_all_inputs()
        st.session_state["show_form"] = False
        st.rerun()
    elif "show_error" in data:
        st.session_state["show_error"] = data["show_error"]
        st.session_state["show_error_msg"] = data["show_error_msg"]
        st.rerun()

# Add New Form
if new_permission:
    if st.button("➕ Add New Customer"):
        st.session_state["show_form"] = True

# Edit Form
if "edit_id" in st.session_state:
    st.session_state["show_form"] = True

if st.session_state["show_form"]:
    customer_form.customer_form(is_edit="edit_id" in st.session_state, submit_callback=customer_form_callback)

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
    if st.session_state["confirmed_action"] == True and "to_delete_customer_id" in st.session_state:
        success = controller.delete_customer(st.session_state["to_delete_customer_id"])

        if success:
            st.session_state["show_success"] = True
            st.session_state["show_success_msg"] = "Deleted successfully."
            del st.session_state["confirmed_action"]
            del st.session_state["to_delete_customer_id"]
        else:
            st.session_state["show_error"] = True
            st.session_state["show_error_msg"] = "Deleting a customer has failed due to some errors."
        st.rerun()
