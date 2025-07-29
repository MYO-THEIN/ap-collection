import streamlit as st
import pandas as pd
import src.customer as controller

@st.dialog("### 🔎 Search Customer")
def search_customer_modal(sel_id: int=None, sel_serial_no: str=None, sel_name: str=None, sel_phone: str=None, sel_delivery_address: str=None, sel_city: str=None, sel_state_region: str=None):
    with st.container():
        search_term = st.text_input(
            label="Search",
            max_chars=5
        )

        customers = controller.get_customers(search_term)
        if customers.shape[0]:
            for customer in customers.iterrows():
                # serial_no, name, phone, delivery_address, city, state_region
                cols = st.columns([1, 1, 1, 2, 1, 1, 1])

                is_selected = sel_id is not None and customer["id"] == sel_id
                cols[0].markdown(f"✔️ {customer['serial_no']}" if is_selected else customer['serial_no'])
                cols[1].markdown(f"✔️ {customer['name']}" if is_selected else customer['name'])
                cols[2].markdown(f"✔️ {customer['phone']}" if is_selected else customer['phone'])
                cols[3].markdown(f"✔️ {customer['delivery_address']}" if is_selected else customer['delivery_address'])
                cols[4].markdown(f"✔️ {customer['city']}" if is_selected else customer['city'])
                cols[5].markdown(f"✔️ {customer['state_region']}" if is_selected else customer['state_region'])

                if cols[6].button("Select", key=f"select_{customer['id']}"):
                    st.session_state["search_id"] = customer["id"]
                    st.session_state["search_serial_no"] = customer["serial_no"]
                    st.session_state["search_name"] = customer["name"]
                    st.session_state["search_phone"] = customer["phone"]
                    st.session_state["search_delivery_address"] = customer["delivery_address"]
                    st.session_state["search_city"] = customer["city"]
                    st.session_state["search_state_region"] = customer["state_region"]
                    st.rerun()
        else:
            st.warning("No data available 📭")

        st.divider()

        if st.button("❌ Close"):
            if sel_id is None:
                if "search_id" not in st.session_state:
                    st.warning("Please select a customer.")
            else:
                if "search_id" not in st.session_state:
                    st.session_state["search_id"] = sel_id
                    st.session_state["search_serial_no"] = sel_serial_no
                    st.session_state["search_name"] = sel_name
                    st.session_state["search_phone"] = sel_phone
                    st.session_state["search_delivery_address"] = sel_delivery_address
                    st.session_state["search_city"] = sel_city
                    st.session_state["search_state_region"] = sel_state_region
                st.rerun()
