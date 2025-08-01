import streamlit as st
import pandas as pd
import src.customer as controller
import forms.customer as customer_form

st.set_page_config(layout="centered")
st.title("🧑 Customers")

if "show_form" not in st.session_state:
    st.session_state["show_form"] = False

# Search
with st.spinner("Searching ..."):
    search_term = st.text_input("🔍 Search Customer")
    data = controller.get_customers(search_term)

    st.write("### Customers")
    if data.shape[0]:
        for idx, row in data.iterrows():
            cols = st.columns([1, 1, 1, 1, 1, 1])
            cols[0].write(f"**{row['serial_no']}**")
            cols[1].write(f"**{row['name']}**")
            cols[2].write(row['city'])
            cols[3].write(row['country'])

            if cols[4].button("✏️ Edit", key=f"edit_{row['id']}", use_container_width=True):
                st.session_state["edit_id"] = row["id"]
                st.session_state["edit_serial_no"] = row["serial_no"]
                st.session_state["edit_name"] = row["name"]
                st.session_state["edit_phone"] = row["phone"]
                st.session_state["edit_home_address"] = row["home_address"]
                st.session_state["edit_delivery_address"] = row["delivery_address"]
                st.session_state["edit_city"] = row["city"]
                st.session_state["edit_state_region"] = row["state_region"]
                st.session_state["edit_country"] = row["country"]

            if cols[5].button("🗑️ Delete", key=f"delete_{row['id']}", use_container_width=True):
                controller.delete_customer(row["id"])
                st.session_state["show_success"] = True
                st.session_state["show_success_msg"] = "Deleted successfully."
                st.rerun()
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
if st.button("➕ Add New Customer"):
    st.session_state["show_form"] = True

# Edit Form
if "edit_id" in st.session_state:
    st.session_state["show_form"] = True

if st.session_state["show_form"]:
    customer_form.customer_form(is_edit="edit_id" in st.session_state, submit_callback=customer_form_callback)

if "show_success" in st.session_state and st.session_state["show_success"]:
    st.success(st.session_state["show_success_msg"], icon=":material/thumb_up:")
elif "show_error" in st.session_state and st.session_state["show_error"]:
    st.error(st.session_state["show_error_msg"], icon=":material/thumb_down:")
