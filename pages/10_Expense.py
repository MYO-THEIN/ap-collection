import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import src.expense as controller
import forms.expense as expense_form
from src.utils import confirmation_dialog

st.set_page_config(layout="centered")

# Authorization
if ("authenticated" not in st.session_state) or ("authenticated" in st.session_state and st.session_state["authenticated"] == False):
    st.session_state.clear()
    st.rerun()
else:
    user_name, role_name = st.session_state["user_name"], st.session_state["role_name"]
    permissions = st.session_state["permissions"]

    if "Expense" in permissions.keys():
        new_permission = permissions["Expense"]["new"]
        edit_permission = permissions["Expense"]["edit"]
        delete_permission = permissions["Expense"]["delete"]

st.title("💸 Expense")

if "show_form" not in st.session_state:
    st.session_state["show_form"] = False

trans_per_page = 10
if "page" not in st.session_state:
    st.session_state["page"] = 1
if "last_filter_mode" not in st.session_state:
    st.session_state["last_filter_mode"] = None
if "last_filter_value" not in st.session_state:
    st.session_state["last_filter_value"] = None

# Search
with st.spinner("Searching ..."):
    data = pd.DataFrame()
    filter_mode = st.radio(label="🔎 Search Expense", options=["Date", "Description"], horizontal=True)
    if filter_mode == "Date":
        col1, col2 = st.columns(2)
        with col1:
            from_date = st.date_input(label="From", label_visibility="collapsed", value=datetime.today() - timedelta(days=6), format="YYYY-MM-DD", key="search_date_from")
        with col2:
            to_date = st.date_input(label="To", label_visibility="collapsed", value=datetime.today(), format="YYYY-MM-DD", key="search_date_to")        

        filter_value = f"{str(from_date)} to {str(to_date)}"
        if from_date and to_date:
            data = controller.get_expenses(from_date=from_date, to_date=to_date, search_term=None)
            
    elif filter_mode == "Description":
        search_term = st.text_input(label="Search Expense", label_visibility="collapsed")
        filter_value = search_term
        if search_term:
            data = controller.get_expenses(from_date=None, to_date=None, search_term=search_term)
            
    # reset pagination if filter changes
    if (filter_mode != st.session_state["last_filter_mode"] or filter_value != st.session_state["last_filter_value"]):
        st.session_state["page"] = 1
    st.session_state["last_filter_mode"] = filter_mode
    st.session_state["last_filter_value"] = filter_value

    st.write("### Expenses")
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
            col1, col2 = st.columns([3, 1], vertical_alignment="center")
            with col1:
                st.markdown(f"**Date**: {row['date']} | **Expense Type**: {row['expense_type_name']} | **Amount**: {row['amount']:,}")
                
            with col2:
                col_edit, col_delete = st.columns(2)
                
                # Edit Button
                with col_edit:
                    if st.button(label="✏️", help="Edit Expense", key=f"edit_{row['id']}", use_container_width=True, disabled=not edit_permission):
                        st.session_state["edit_id"] = row["id"]
                        st.session_state["edit_date"] = row["date"]
                        st.session_state["edit_expense_type_id"] = row["expense_type_id"]
                        st.session_state["edit_expense_type_name"] = row["expense_type_name"]
                        st.session_state["edit_description"] = row["description"]
                        st.session_state["edit_amount"] = row["amount"]

                # Delete Button
                with col_delete:
                    if st.button(label="🗑️", help="Delete Expense", key=f"delete_{row['id']}", use_container_width=True, disabled=not delete_permission):
                        st.session_state["to_delete_expense_id"] = row["id"]
                        confirmation_dialog(
                            msg="Are you sure to delete this expense?", 
                            yes_button_txt="✅ Yes, delete", 
                            no_button_txt="❌ Cancel"
                        )

            with st.expander(label="📋 Description"):
                if row["description"]:
                    st.markdown(row["description"].replace("\n", "<br>"), unsafe_allow_html=True)
                else:
                    st.markdown("No data available 📭")

            st.divider()
    else:
        st.info("No data available 📭")
        st.divider()


def clear_all_inputs():
    # Add New
    add_new_keys = [
        "date", "expense_type_id", "description", "amount"
    ]
    for key in add_new_keys:
        if key in st.session_state:
            del st.session_state[key]

    # Edit
    edit_keys = [
        "edit_id", "edit_date", "edit_expense_type_id", "edit_description", "edit_amount"
    ]
    for key in edit_keys:
        if key in st.session_state:
            del st.session_state[key]

def expense_form_callback(data=None):
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
    if st.button("➕ Add New Expense"):
        clear_all_inputs()
        st.session_state["show_form"] = True

# Edit Form
if "edit_id" in st.session_state:
    st.session_state["show_form"] = True

if st.session_state["show_form"]:
    expense_form.expense_form(is_edit="edit_id" in st.session_state, submit_callback=expense_form_callback)

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
    if st.session_state["confirmed_action"] == True and "to_delete_expense_id" in st.session_state:
        success = controller.delete_expense(st.session_state["to_delete_expense_id"])

        if success:
            st.session_state["show_success"] = True
            st.session_state["show_success_msg"] = "Deleted successfully."
            del st.session_state["confirmed_action"]
            del st.session_state["to_delete_expense_id"]
        else:
            st.session_state["show_error"] = True
            st.session_state["show_error_msg"] = "Deleting an expense has failed due to some errors."
        st.rerun()
