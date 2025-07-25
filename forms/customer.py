import streamlit as st

def add_new_form(submit_callback=None):
    with st.form("add_form", enter_to_submit=False, clear_on_submit=True):
        serial_no = st.text_input(label="Serial No.", max_chars=5)
        name = st.text_input(label="Name", max_chars=50)
        phone = st.text_input(label="Phone", max_chars=50)
        home_address = st.text_area(label="Home Address", max_chars=200)
        delivery_address = st.text_area(label="Delivery Address", max_chars=200)
        city = st.selectbox(label="City", options=None)
        state_region = st.selectbox(label="State/Region", options=None)

        submitted = st.form_submit_button("Add")
        if submitted:
            # save the data here

            if submit_callback:
                submit_callback({
                    "serial_no": serial_no,
                    "name": name,
                    "phone": phone
                })
