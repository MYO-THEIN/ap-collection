import streamlit as st
from datetime import datetime
from src.expense_type import get_expense_types
import src.expense as controller

def expense_form(is_edit: bool, submit_callback=None):
    expense_types = get_expense_types()
    
    st.subheader("🧾 Expense Info")

    dt = st.date_input(
        label="Date", 
        value=datetime.today() if not is_edit else st.session_state["edit_date"],
        format="YYYY-MM-DD"
    )

    expense_type_name = st.selectbox(
        label="Expense Type",
        options=expense_types["name"].tolist(),
        accept_new_options=False,
        index=expense_types["name"].tolist().index(st.session_state["edit_expense_type_name"]) if is_edit else None
    )
    if expense_type_name:
        expense_type_id = int(expense_types[expense_types["name"] == expense_type_name].iloc[0]["id"])
    
    description = st.text_area(
        label="Description",
        value=None if not is_edit else st.session_state["edit_description"],
        height="content"
    )

    amount = st.number_input(
        label="Amount",
        min_value=0,
        value=st.session_state["edit_amount"] if is_edit else 0
    )
  
    # Save
    if st.button("✅ Confirm Expense" if not is_edit else "💾 Save Expense"):
        if expense_type_id is None:
            st.warning("Select a expense type.")
        else:
            expense = {
                "id": st.session_state["edit_id"] if is_edit else None,
                "date": dt,
                "expense_type_id": expense_type_id,
                "description": description,
                "amount": amount
            }

            if is_edit:
                success = controller.update_expense(expense=expense)
                msg = "Updated successfully." if success else "Updating an expense failed."
            else:
                success = controller.add_expense(expense=expense)
                msg = "Added successfully." if success else "Adding an expense failed."

            if success:
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
