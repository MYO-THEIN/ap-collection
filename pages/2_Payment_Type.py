import streamlit as st
import pandas as pd
import src.payment_type as controller

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

st.set_page_config(layout="centered")
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
                controller.delete_payment_type(row["id"])
                st.session_state["show_success"] = True
                st.session_state["show_success_msg"] = "Deleted successfully."
                st.rerun()
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
