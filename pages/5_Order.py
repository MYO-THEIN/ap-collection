import streamlit as st
import pandas as pd
from datetime import datetime 
import src.order as controller
import forms.order as order_form

st.title("🛒 Orders")


# Search
with st.spinner("Searching ..."):
    cols = st.columns([1, 3])
    dt = cols[0].date_input(label="Date", value=datetime.today(), format="YYYY-MM-DD", key="search_date")
    search_term = cols[1].text_input("🔍 Search Order")
    
    # orders
    data = controller.get_orders(dt=dt, search_term=search_term)
    # order_items
    order_ids = []
    if data is not None:
        order_ids = data["id"].tolist()
    data_items = controller.get_order_items(dt=dt, order_ids=order_ids)

    st.write("### Orders")
    if data.shape[0]:
        for row in data.iterrows():
            st.markdown(f"**Date**: {row['date']} | **Order No.**: {row['order_no']} | **Customer**: {row['customer_serial_no']} {row['customer_name']} | **Quantity**: {row['ttl_quantity']} | **Amount**: {row['ttl_amount']}")
            items = data_items[data_items["order_id"] == row["id"]]
            st.dataframe(data=items)
            st.markdown("---")
    else:
        st.info("No data available 📭")


if "show_form" not in st.session_state:
    st.session_state["show_form"] = False


def order_form_callback(data=None):
    if "show_success" in data:
        st.session_state["show_success"] = data["show_success"]
        st.session_state["show_success_msg"] = data["show_success_msg"]
        st.session_state["show_form"] = False
        st.rerun()


# Add New Form
if st.button("➕ Add New Order"):
    st.session_state["show_form"] = True


# Edit Form
if "edit_id" in st.session_state:
    st.session_state["show_form"] = True


if st.session_state["show_form"]:
    order_form.order_form(is_edit="edit_id" in st.session_state, submit_callback=order_form_callback)

if "show_success" in st.session_state and st.session_state["show_success"]:
    st.success(st.session_state["show_success_msg"], icon=":material/thumb_up:")
