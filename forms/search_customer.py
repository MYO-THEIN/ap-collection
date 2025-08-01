import streamlit as st
import pandas as pd
import src.customer as controller

@st.dialog("### 🔎 Search Customer", width="large")
def search_customer_modal(sel_id: int=None, sel_serial_no: str=None, sel_name: str=None, sel_phone: str=None, sel_delivery_address: str=None, sel_city: str=None, sel_state_region: str=None):
    with st.container():
        search_term = st.text_input(
            label="Search",
            max_chars=5
        )

        customers = controller.get_customers(search_term)
        if customers.shape[0]:
            for _, customer in customers.iterrows():
                is_selected = sel_id is not None and customer["id"] == sel_id
                # serial_no, name, phone
                st.markdown(
                    f"""
                    {'✔️' + customer['serial_no'] if is_selected else customer['serial_no']} |
                    {customer['name'] if is_selected else customer['name']} |
                    {customer['phone'] if is_selected else customer['phone']}
                    """
                )
                # delivery_address
                st.markdown(customer['delivery_address'] if is_selected else customer['delivery_address'])
                # city, state_region
                st.markdown(
                    f"""
                    {customer['city'] if is_selected else customer['city']} |
                    {customer['state_region'] if is_selected else customer['state_region']}
                    """
                )
                
                if st.button("👉 Select", key=f"select_{customer['id']}"):
                    st.session_state["search_id"] = customer["id"]
                    st.session_state["search_serial_no"] = customer["serial_no"]
                    st.session_state["search_name"] = customer["name"]
                    st.session_state["search_phone"] = customer["phone"]
                    st.session_state["search_delivery_address"] = customer["delivery_address"]
                    st.session_state["search_city"] = customer["city"]
                    st.session_state["search_state_region"] = customer["state_region"]
                    st.rerun()

                st.markdown("-----")
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
