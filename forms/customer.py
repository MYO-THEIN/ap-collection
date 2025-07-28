import streamlit as st
import pandas as pd
import json
import src.customer as controller
import forms.search_city as search_city

# Country
countries = [
    "N/A",
    "Cambodia",
    "China",
    "India",
    "Japan",
    "Laos",
    "Malaysia",
    "Myanmar",
    "Singapore",
    "Thailand",
    "Vietnam"
]

def customer_form(is_edit: bool, submit_callback=None):
    with st.form(key="add_new_form" if is_edit else "edit_form", enter_to_submit=False):
        serial_no = st.text_input(
            label="Serial No.", 
            max_chars=5,
            key="serial_no" if not is_edit else "edit_serial_no"
        )

        name = st.text_input(
            label="Name", 
            max_chars=50, 
            key="name" if not is_edit else "edit_name"
        )

        phone = st.text_input(
            label="Phone", 
            max_chars=50,
            key="phone" if not is_edit else "edit_phone"
        )

        home_address = st.text_area(
            label="Home Address", 
            max_chars=200,
            key="home_address" if not is_edit else "edit_home_address"
        )

        delivery_address = st.text_area(
            label="Delivery Address", 
            max_chars=200,
            key="delivery_address" if not is_edit else "edit_delivery_address"
        )

        # 3 columns for Search, City, State/Region
        left, middle, right = st.columns(3, vertical_alignment="bottom")
        search_city_submit = left.form_submit_button("🔎 City, State/Region", use_container_width=True)
        if search_city_submit:
            search_city.search_city_modal(
                sel_city=st.session_state["search_city"] if "search_city" in st.session_state else None,
                sel_state=st.session_state["search_state_region"] if "search_state_region" in st.session_state else None
            )
        city = middle.text_input(
            label="City",
            value=st.session_state["search_city"] if "search_city" in st.session_state else "N/A",
            disabled=True,
            label_visibility="collapsed"
        )
        state_region = right.text_input(
            label="State/Region",
            value=st.session_state['search_state_region'] if 'search_state_region' in st.session_state else 'N/A',
            disabled=True,
            label_visibility="collapsed"
        )
        
        # Country
        country = st.selectbox(
            label="Country", 
            options=countries, 
            key="country" if not is_edit else "edit_country",
            accept_new_options=False
        )

        if st.form_submit_button("Save"):
            if serial_no.strip() and name.strip():
                if is_edit:
                    success = controller.update_customer(
                        st.session_state["edit_id"],
                        serial_no, name, phone, home_address, delivery_address,
                        city, state_region, country
                    )
                    msg = "Updated successfully."
                else:
                    success = controller.add_customer(
                        serial_no, name, phone, home_address, delivery_address,
                        city, state_region, country
                    )
                    msg = "Added successfully."

                if success:
                    st.session_state["show_success"] = True
                    st.session_state["show_success_message"] = msg
                    if submit_callback:
                        submit_callback({
                            "show_success": True,
                            "show_success_msg": msg
                        })
            else:
                st.warning("Serial No. and Name cannot be empty.")
