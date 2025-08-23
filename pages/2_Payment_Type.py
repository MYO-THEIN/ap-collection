import streamlit as st
import pandas as pd
import src.payment_type as controller
from src.utils import confirmation_dialog

st.set_page_config(layout="centered")

# Authorization
if st.session_state["authenticated"] == False:
    st.session_state.clear()
    st.rerun()
else:
    user_name, role_name = st.session_state["user_name"], st.session_state["role_name"]
    permissions = st.session_state["permissions"]

    if "Payment Type" in permissions.keys():
        new_permission = permissions["Payment Type"]["new"]
        edit_permission = permissions["Payment Type"]["edit"]
        delete_permission = permissions["Payment Type"]["delete"]

st.title("💰 Payment Types")

# Search
with st.spinner("Searching ..."):
    search_term = st.text_input("🔍 Search Payment Type")
    data = controller.get_payment_types(search_term)

    st.write("### Payment Types")
    if data.shape[0]:
        for idx, row in data.iterrows():
            cols = st.columns([3, 1, 1])
            cols[0].write(f"**{row['name']}**")

            if cols[1].button("✏️ Edit", key=f"edit_{row['id']}", use_container_width=True, disabled=not edit_permission):
                st.session_state["edit_id"] = row["id"]
                st.session_state["edit_name"] = row["name"]

            if cols[2].button("🗑️ Delete", key=f"delete_{row['id']}", use_container_width=True, disabled=not delete_permission):
                st.session_state["to_delete_payment_type_id"] = row["id"]
                confirmation_dialog(
                    msg="Are you sure to delete this payment type?", 
                    yes_button_txt="✅ Yes, delete", 
                    no_button_txt="❌ Cancel"
                )
    else:
        st.write("No data available 📭")

st.divider()


# Edit Form
if "edit_id" in st.session_state:
    with st.form("edit_form", enter_to_submit=False, clear_on_submit=True):
        new_name = st.text_input(label="Name", value=st.session_state["edit_name"], max_chars=50)
        submitted = st.form_submit_button("💾 Save")
        if submitted:
            if new_name.strip():
                success = controller.update_payment_type(st.session_state["edit_id"], new_name)
                if success:
                    for key in ["edit_id", "edit_name"]:
                        del st.session_state[key]
                    st.session_state["show_success"] = True
                    st.session_state["show_success_msg"] = "Updated successfully."
                    st.rerun()
            else:
                st.warning("Name cannot be empty.")

# Add New Form
if new_permission:
    with st.expander("➕ Add New Payment Type"):
        with st.form("add_form", enter_to_submit=False, clear_on_submit=True):
            new_name = st.text_input(label="Name", max_chars=50)
            submitted = st.form_submit_button("💾 Add")
            if submitted:
                if new_name.strip():
                    success = controller.add_payment_type(new_name.strip())
                    if success:
                        st.session_state["show_success"] = True
                        st.session_state["show_success_msg"] = "Added successfully."
                        st.rerun()
                else:
                    st.warning("Name cannot be empty.")

if "show_success" in st.session_state and st.session_state["show_success"]:
    st.success(st.session_state["show_success_msg"], icon=":material/thumb_up:")
    del st.session_state["show_success"]
    del st.session_state["show_success_msg"]

# Delete confirmed and good to go 
if "confirmed_action" in st.session_state:
    if st.session_state["confirmed_action"] == True and "to_delete_payment_type_id" in st.session_state:
        success = controller.delete_payment_type(st.session_state["to_delete_payment_type_id"])

        if success:
            st.session_state["show_success"] = True
            st.session_state["show_success_msg"] = "Deleted successfully."
            del st.session_state["confirmed_action"]
            del st.session_state["to_delete_payment_type_id"]
        else:
            st.session_state["show_error"] = True
            st.session_state["show_error_msg"] = "Deleting a payment type has failed due to some errors."
        st.rerun()
