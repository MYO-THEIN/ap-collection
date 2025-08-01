import streamlit as st
import json
import src.customer as controller

with open("data/cities_states_regions.json", "r", encoding="utf-8") as f:
    json_data = json.load(f)

# State/Region
states_regions = sorted(list(json_data.keys()))

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
    st.session_state["submitted"] = False

    col1, col2 = st.columns(2)
    with col1:
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
            
            # setting default country
            if not is_edit:
                st.session_state["country"] = "Myanmar"

            country = st.selectbox(
                label="Country", 
                options=countries, 
                key="country" if not is_edit else "edit_country",
                accept_new_options=False
            )

            if st.form_submit_button("💾 Save"):
                st.session_state["submitted"] = True

    with col2:
        # setting default city, state_region
        if not is_edit:
            st.session_state["state_region"] = "မန္တလေးတိုင်းဒေသကြီး"
            st.session_state["city"] = "မန္တလေး"

        state_region = st.selectbox(
            label="State/Region",
            options=states_regions,
            key="state_region" if not is_edit else "edit_state_region",
            accept_new_options=False
        )
        if state_region:
            cities = [city["burmese"] for city in json_data[state_region]]
   
        city = st.selectbox(
            label="City",
            options=cities,
            key="city" if not is_edit else "edit_city",
            accept_new_options=False
        )

    if "submitted" in st.session_state and st.session_state["submitted"]:
        if serial_no.strip() and name.strip():
            if is_edit:
                result = controller.update_customer(
                    st.session_state["edit_id"],
                    serial_no, name, phone, home_address, delivery_address,
                    city, state_region, country
                )
            else:
                result = controller.add_customer(
                    serial_no, name, phone, home_address, delivery_address,
                    city, state_region, country
                )

            del st.session_state["submitted"]

            if result["success"]:
                msg = "Added successfully." if not is_edit else "Updated successfully."
                submit_callback({
                    "show_success": True,
                    "show_success_msg": msg,
                    "new_id": result["new_id"] if not is_edit else None
                })
            else:
                submit_callback({
                    "show_error": True,
                    "show_error_msg": result["error"]
                })
        else:
            st.warning("Serial No. and Name cannot be empty.")
